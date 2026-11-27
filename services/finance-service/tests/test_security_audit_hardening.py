"""AUTH-1..AUTH-4 verification tests for Finance Service (unauthenticated, IDOR, RBAC)."""

from __future__ import annotations

import json
import uuid
from datetime import date, UTC, datetime, timedelta
from decimal import Decimal

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints.health import get_db
from app.core.config import settings
from app.db.base import Base
from app.domain.models import Invoice, Payment, PaymentIntent, Receipt, StudentFinancialAccount
from app.main import app
from app.security import auth as finance_auth


@pytest.fixture()
def finance_env(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk["kid"] = "fin-test-1"
    monkeypatch.setattr(finance_auth, "_get_jwks", lambda: {"keys": [jwk]})
    monkeypatch.setattr(settings, "JWT_ISSUER", "http://localhost:8001")
    monkeypatch.setattr(settings, "JWT_AUDIENCE", "smart-education-api")
    monkeypatch.setattr(settings, "JWT_ALGORITHMS", ["RS256"])

    session = SessionLocal()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    def make_token(user_id: uuid.UUID, roles: list[str], *, typ: str = "at+jwt", permissions: list[str] | None = None):
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "roles": roles,
            "permissions": permissions or [],
            "jti": uuid.uuid4().hex,
            "iss": "http://localhost:8001",
            "aud": "smart-education-api",
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=15),
        }
        return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "fin-test-1", "typ": typ})

    with TestClient(app) as client:
        yield client, session, make_token

    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_finance_unauthenticated_idor_and_rbac(finance_env):
    client, db, make_token = finance_env
    student_a = uuid.uuid4()
    student_b = uuid.uuid4()
    teacher_id = uuid.uuid4()
    admin_id = uuid.uuid4()

    acct_b = StudentFinancialAccount(
        student_user_id=student_b,
        account_number="ACC-B-001",
        outstanding_balance=Decimal("1000.00"),
    )
    db.add(acct_b)
    db.flush()

    inv_b = Invoice(
        invoice_number="INV-B-001",
        account_id=acct_b.id,
        student_user_id=student_b,
        program_id=uuid.uuid4(),
        academic_year_id=uuid.uuid4(),
        semester_number=1,
        issue_date=date(2026, 11, 1),
        due_date=date(2026, 12, 1),
        subtotal=Decimal("1000.00"),
        total_amount=Decimal("1000.00"),
        balance_amount=Decimal("1000.00"),
        status="ISSUED",
    )
    db.add(inv_b)
    db.flush()

    intent_b = PaymentIntent(
        student_user_id=student_b,
        invoice_id=inv_b.id,
        amount=Decimal("500.00"),
        currency="PKR",
        provider="JAZZ_CASH",
        status="PENDING",
        expires_at=datetime.now(UTC) + timedelta(hours=2),
    )
    db.add(intent_b)
    db.flush()

    pay_b = Payment(
        payment_intent_id=intent_b.id,
        student_user_id=student_b,
        amount=Decimal("500.00"),
        currency="PKR",
        method="JAZZ_CASH",
        provider_transaction_id="TXN-B-1",
        status="CONFIRMED",
        paid_at=datetime.now(UTC),
        receipt_number="REC-B-1",
    )
    db.add(pay_b)
    db.flush()

    rec_b = Receipt(
        receipt_number="REC-B-1",
        payment_id=pay_b.id,
        student_user_id=student_b,
        amount=Decimal("500.00"),
        currency="PKR",
        issued_at=datetime.now(UTC),
        receipt_data={"invoice_number": "INV-B-001"},
    )
    db.add(rec_b)
    db.commit()

    # 1. AUTH-1: Unauthenticated returns 401
    for path in [
        "/api/v1/invoices",
        f"/api/v1/invoices/{inv_b.id}",
        "/api/v1/payments",
        "/api/v1/student-accounts",
        "/api/v1/reports/overview",
    ]:
        assert client.get(path).status_code == 401

    # 2. AUTH-4: Refresh token typ rejected
    rt_headers = {"Authorization": f"Bearer {make_token(admin_id, ['admin'], typ='rt+jwt')}"}
    assert client.get("/api/v1/reports/overview", headers=rt_headers).status_code == 401

    # 3. AUTH-2: Student A cannot access Student B's records or create/simulate intents against B
    h_a = {"Authorization": f"Bearer {make_token(student_a, ['student'])}"}
    assert client.get(f"/api/v1/invoices/{inv_b.id}", headers=h_a).status_code == 403
    assert client.get(f"/api/v1/payments/{pay_b.id}", headers=h_a).status_code == 403
    assert client.get(f"/api/v1/payments/receipts/{rec_b.id}", headers=h_a).status_code == 403
    assert client.get(f"/api/v1/student-accounts/by-user/{student_b}", headers=h_a).status_code == 403
    assert client.get(f"/api/v1/student-accounts/{acct_b.id}", headers=h_a).status_code == 403
    assert client.post(
        "/api/v1/payments/intent",
        headers=h_a,
        json={"invoice_id": str(inv_b.id), "amount": "100.00", "provider": "JAZZ_CASH"},
    ).status_code == 403
    assert client.post(
        "/api/v1/payments/simulate",
        headers=h_a,
        json={"payment_intent_id": str(intent_b.id)},
    ).status_code == 403

    # 4. AUTH-2 & AUTH-3: Teacher cannot access Student B's invoices/accounts or admin reports
    h_t = {"Authorization": f"Bearer {make_token(teacher_id, ['teacher'])}"}
    assert client.get(f"/api/v1/invoices/{inv_b.id}", headers=h_t).status_code == 403
    assert client.get("/api/v1/student-accounts", headers=h_t).status_code == 403
    assert client.get("/api/v1/reports/overview", headers=h_t).status_code == 403

    # 5. AUTH-3: Admin can view overview & student record
    h_admin = {"Authorization": f"Bearer {make_token(admin_id, ['admin'])}"}
    assert client.get("/api/v1/reports/overview", headers=h_admin).status_code == 200
    assert client.get(f"/api/v1/invoices/{inv_b.id}", headers=h_admin).status_code == 200
