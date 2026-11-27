"""Database-backed lockout and fixed-window rate limiting fallback when Redis is absent."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from smartedu_security.lockout import LockoutDecision
from smartedu_security.rate_limit import RateLimitDecision
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import AuthRateLimitBucket, LoginLockoutBucket


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _digest_key(raw: str) -> str:
    return hashlib.sha256(raw.strip().casefold().encode("utf-8")).hexdigest()


class DatabaseFixedWindowLimiter:
    """Persistent fixed-window rate limiter backed by Identity's SQL database."""

    def __init__(self, session_factory: Callable[[], Session] | None = None):
        self.session_factory = session_factory

    def hit_sync(
        self,
        db: Session,
        key: str,
        *,
        limit: int,
        window_seconds: int,
    ) -> RateLimitDecision:
        now = _utcnow()
        bucket_key = _digest_key(key)
        row = db.scalar(
            select(AuthRateLimitBucket)
            .where(AuthRateLimitBucket.bucket_key == bucket_key)
            .with_for_update()
        )
        if row is None or _aware(row.window_expires_at) <= now:
            expires_at = now + timedelta(seconds=window_seconds)
            if row is None:
                row = AuthRateLimitBucket(
                    bucket_key=bucket_key,
                    count=1,
                    window_expires_at=expires_at,
                )
                db.add(row)
            else:
                row.count = 1
                row.window_expires_at = expires_at
        else:
            row.count += 1
        db.commit()

        allowed = row.count <= limit
        remaining = max(0, limit - row.count)
        retry_after = 0 if allowed else max(1, int((_aware(row.window_expires_at) - now).total_seconds()))
        return RateLimitDecision(
            allowed=allowed,
            remaining=remaining,
            retry_after_seconds=retry_after,
        )

    async def hit(
        self,
        key: str,
        *,
        limit: int,
        window_seconds: int,
        db: Session | None = None,
    ) -> RateLimitDecision:
        if db is not None:
            return self.hit_sync(db, key, limit=limit, window_seconds=window_seconds)
        with self.session_factory() as session:
            return self.hit_sync(session, key, limit=limit, window_seconds=window_seconds)


class DatabaseLockoutStore:
    """Persistent login lockout store backed by Identity's SQL database."""

    def __init__(
        self,
        session_factory: Callable[[], Session],
        *,
        max_failures: int = 5,
        failure_window_seconds: int = 900,
        lock_seconds: int = 900,
    ):
        self.session_factory = session_factory
        self.max_failures = max_failures
        self.failure_window_seconds = failure_window_seconds
        self.lock_seconds = lock_seconds

    def _check_sync(self, db: Session, subject: str) -> LockoutDecision:
        now = _utcnow()
        key = _digest_key(subject)
        row = db.scalar(select(LoginLockoutBucket).where(LoginLockoutBucket.subject_key == key))
        if row is None:
            return LockoutDecision(allowed=True, failure_count=0)
        if row.locked_until is not None and _aware(row.locked_until) > now:
            return LockoutDecision(
                allowed=False,
                retry_after_seconds=max(1, int((_aware(row.locked_until) - now).total_seconds())),
                failure_count=row.failure_count,
            )
        if _aware(row.window_expires_at) <= now:
            return LockoutDecision(allowed=True, failure_count=0)
        return LockoutDecision(allowed=True, failure_count=row.failure_count)

    def _failure_sync(self, db: Session, subject: str) -> LockoutDecision:
        now = _utcnow()
        key = _digest_key(subject)
        row = db.scalar(
            select(LoginLockoutBucket)
            .where(LoginLockoutBucket.subject_key == key)
            .with_for_update()
        )
        if row is None or _aware(row.window_expires_at) <= now:
            expires_at = now + timedelta(seconds=self.failure_window_seconds)
            if row is None:
                row = LoginLockoutBucket(
                    subject_key=key,
                    failure_count=1,
                    window_expires_at=expires_at,
                    locked_until=None,
                )
                db.add(row)
            else:
                row.failure_count = 1
                row.window_expires_at = expires_at
                row.locked_until = None
        else:
            row.failure_count += 1
            row.window_expires_at = now + timedelta(seconds=self.failure_window_seconds)

        if row.failure_count >= self.max_failures:
            row.locked_until = now + timedelta(seconds=self.lock_seconds)
            db.commit()
            return LockoutDecision(
                allowed=False,
                retry_after_seconds=self.lock_seconds,
                failure_count=row.failure_count,
            )

        db.commit()
        return LockoutDecision(allowed=True, failure_count=row.failure_count)

    def _success_sync(self, db: Session, subject: str) -> None:
        key = _digest_key(subject)
        db.execute(delete(LoginLockoutBucket).where(LoginLockoutBucket.subject_key == key))
        db.commit()

    async def check(self, subject: str, db: Session | None = None) -> LockoutDecision:
        if db is not None:
            return self._check_sync(db, subject)
        with self.session_factory() as session:
            return self._check_sync(session, subject)

    async def failure(self, subject: str, db: Session | None = None) -> LockoutDecision:
        if db is not None:
            return self._failure_sync(db, subject)
        with self.session_factory() as session:
            return self._failure_sync(session, subject)

    async def success(self, subject: str, db: Session | None = None) -> None:
        if db is not None:
            self._success_sync(db, subject)
            return
        with self.session_factory() as session:
            self._success_sync(session, subject)
