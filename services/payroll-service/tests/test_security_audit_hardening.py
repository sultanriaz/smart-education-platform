"""AUTH-1..AUTH-4 verification tests for Payroll Service (unauthenticated, employee IDOR, RBAC)."""

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
from app.domain.models import EmployeePayrollProfile, PayrollPeriod, PayrollRun, PayrollRunItem, Payslip
from app.main import app
from app.security import auth as payroll_auth


@pytest.fixture()
def payroll_env(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base_cls = EmployeePayrollProfile.metadata
    Base_cls.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk["kid"] = "pay-test-1"
    monkeypatch.setattr(payroll_auth, "_get_jwks", lambda: {"keys": [jwk]})
    monkeypatch.setattr(settings, "JWT_ISSUER", "http://localhost:8001")
    monkeypatch.setattr(settings, "JWT_AUDIENCE", "smart-education-api")
    monkeypatch.setattr(settings, "JWT_ALGORITHMS", ["RS256"])

    session = SessionLocal()
    app.dependency_overrides[get_db] = lambda: session

    def make_token(user_id: uuid.UUID, roles: list[str], *, typ: str = "at+jwt"):
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "roles": roles,
            "permissions": [],
            "jti": uuid.uuid4().hex,
            "iss": "http://localhost:8001",
            "aud": "smart-education-api",
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=15),
        }
        return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "pay-test-1", "typ": typ})

    with TestClient(app) as client:
        yield client, session, make_token

    app.dependency_overrides.clear()
    session.close()
    Base_cls.drop_all(bind=engine)


def test_payroll_unauthenticated_employee_idor_and_admin_rbac(payroll_env):
    client, db, make_token = payroll_env
    emp_a = uuid.uuid4()
    emp_b = uuid.uuid4()
    admin_id = uuid.uuid4()

    profile_b = EmployeePayrollProfile(
        user_id=emp_b,
        employee_number="EMP-002",
        full_name="Employee B",
        email="empb@example.edu",
        designation="Lecturer",
        employment_type="FULL_TIME",
        department_id=uuid.uuid4(),
        bank_account_number="PK00HABB000000001",
        is_active=True,
    )
    db.add(profile_b)
    db.flush()

    period = PayrollPeriod(
        year=2026,
        month=11,
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 30),
        status="OPEN",
    )
    db.add(period)
    db.flush()

    run = PayrollRun(
        period_id=period.id,
        run_number="RUN-2026-11",
        status="APPROVED",
        total_gross=Decimal("100000.00"),
        total_deductions=Decimal("5000.00"),
        total_net=Decimal("95000.00"),
        created_by_user_id=admin_id,
    )
    db.add(run)
    db.flush()

    run_item = PayrollRunItem(
        payroll_run_id=run.id,
        employee_profile_id=profile_b.id,
        base_salary=Decimal("90000.00"),
        total_allowances=Decimal("10000.00"),
        total_deductions=Decimal("5000.00"),
        gross_salary=Decimal("100000.00"),
        net_salary=Decimal("95000.00"),
    )
    db.add(run_item)
    db.flush()

    slip_b = Payslip(
        payslip_number="PS-002",
        payroll_run_item_id=run_item.id,
        period_id=period.id,
        employee_profile_id=profile_b.id,
        gross_salary=Decimal("100000.00"),
        net_salary=Decimal("95000.00"),
        issue_date=date(2026, 11, 30),
        is_published=True,
        breakdown={"components": []},
    )
    db.add(slip_b)
    db.commit()

    # 1. AUTH-1: Unauthenticated rejected with 401
    for path in [
        "/api/v1/payslips/my-payslips",
        f"/api/v1/payslips/{slip_b.id}",
        "/api/v1/profiles",
        "/api/v1/runs",
    ]:
        assert client.get(path).status_code == 401

    # 2. AUTH-2: Employee A ("employee" role) CANNOT read or download Employee B's payslip or profile!
    h_emp_a = {"Authorization": f"Bearer {make_token(emp_a, ['employee'])}"}
    assert client.get(f"/api/v1/payslips/{slip_b.id}", headers=h_emp_a).status_code == 403
    assert client.get(f"/api/v1/payslips/{slip_b.id}/download", headers=h_emp_a).status_code == 403
    assert client.get(f"/api/v1/profiles/by-user/{emp_b}", headers=h_emp_a).status_code == 403

    # 3. AUTH-3: Non-admin employee cannot list all profiles or runs
    assert client.get("/api/v1/profiles", headers=h_emp_a).status_code == 403
    assert client.get("/api/v1/runs", headers=h_emp_a).status_code == 403

    # 4. Employee B can read own payslip & profile; Admin can read any
    h_emp_b = {"Authorization": f"Bearer {make_token(emp_b, ['employee'])}"}
    assert client.get(f"/api/v1/payslips/{slip_b.id}", headers=h_emp_b).status_code == 200
    assert client.get(f"/api/v1/profiles/by-user/{emp_b}", headers=h_emp_b).status_code == 200
    h_admin = {"Authorization": f"Bearer {make_token(admin_id, ['admin'])}"}
    assert client.get(f"/api/v1/payslips/{slip_b.id}", headers=h_admin).status_code == 200
