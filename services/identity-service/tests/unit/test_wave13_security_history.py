"""Wave 13 audit persistence and own-user scoping (SQLite)."""
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories.audit_repository import AuditRepository


def test_security_audit_redacts_secrets_and_bounds_user_history():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        repo = AuditRepository(db)
        alice, bob = uuid.uuid4(), uuid.uuid4()
        repo.record(action="auth.login_failed", user_id=alice, details={"password": "danger", "nested": {"refresh_token": "secret", "request": "ok"}})
        repo.record(action="auth.login_succeeded", user_id=bob)
        db.commit()
        own = repo.history(user_id=alice)
        assert len(own) == 1
        assert own[0].outcome == "FAILED"
        assert own[0].details["password"] == "[REDACTED]"
        assert own[0].details["nested"]["refresh_token"] == "[REDACTED]"
        assert repo.history(user_id=alice, outcome="SUCCEEDED") == []
        assert len(repo.history(limit=1)) == 1
