from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class EmployeePayrollProfile(Base):
    __tablename__ = "employee_payroll_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    employee_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(160), index=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    designation: Mapped[str] = mapped_column(String(100))
    employment_type: Mapped[str] = mapped_column(String(50), default="FULL_TIME")  # FULL_TIME, PART_TIME, CONTRACT
    bank_name: Mapped[str] = mapped_column(String(100), default="Habib Bank Limited")
    bank_account_number: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    salary_structures: Mapped[list[SalaryStructure]] = relationship(
        "SalaryStructure", back_populates="employee_profile", cascade="all, delete-orphan"
    )
    payslips: Mapped[list[Payslip]] = relationship("Payslip", back_populates="employee_profile")


class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("employee_payroll_profiles.id", ondelete="CASCADE"), index=True
    )
    effective_from: Mapped[date] = mapped_column(Date, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    employee_profile: Mapped[EmployeePayrollProfile] = relationship(
        "EmployeePayrollProfile", back_populates="salary_structures"
    )
    components: Mapped[list[SalaryComponent]] = relationship(
        "SalaryComponent", back_populates="salary_structure", cascade="all, delete-orphan"
    )


class SalaryComponent(Base):
    __tablename__ = "salary_components"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    salary_structure_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("salary_structures.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    component_type: Mapped[str] = mapped_column(String(50))  # ALLOWANCE, DEDUCTION
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_percentage: Mapped[bool] = mapped_column(Boolean, default=False)
    percentage_value: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)

    salary_structure: Mapped[SalaryStructure] = relationship("SalaryStructure", back_populates="components")


class PayrollPeriod(Base):
    __tablename__ = "payroll_periods"
    __table_args__ = (
        UniqueConstraint("year", "month", name="uq_payroll_period_year_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year: Mapped[int] = mapped_column(Integer, index=True)
    month: Mapped[int] = mapped_column(Integer, index=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", index=True)  # OPEN, PROCESSING, CLOSED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    runs: Mapped[list[PayrollRun]] = relationship("PayrollRun", back_populates="period")


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payroll_periods.id"), index=True
    )
    run_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    status: Mapped[str] = mapped_column(
        String(30), default="DRAFT", index=True
    )  # DRAFT, CALCULATED, REVIEWED, APPROVED, DISBURSEMENT_PENDING, PAID, REJECTED
    total_gross: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    total_net: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    period: Mapped[PayrollPeriod] = relationship("PayrollPeriod", back_populates="runs")
    items: Mapped[list[PayrollRunItem]] = relationship(
        "PayrollRunItem", back_populates="payroll_run", cascade="all, delete-orphan"
    )
    disbursement_batches: Mapped[list[DisbursementBatch]] = relationship("DisbursementBatch", back_populates="payroll_run")


class PayrollRunItem(Base):
    __tablename__ = "payroll_run_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payroll_runs.id", ondelete="CASCADE"), index=True
    )
    employee_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("employee_payroll_profiles.id"), index=True
    )
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total_allowances: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    net_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    days_worked: Mapped[int] = mapped_column(Integer, default=30)
    proration_factor: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("1.0000"))
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    payroll_run: Mapped[PayrollRun] = relationship("PayrollRun", back_populates="items")
    employee_profile: Mapped[EmployeePayrollProfile] = relationship("EmployeePayrollProfile")
    payslip: Mapped[Payslip | None] = relationship("Payslip", back_populates="run_item", uselist=False)


class DisbursementBatch(Base):
    __tablename__ = "disbursement_batches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payroll_runs.id"), index=True
    )
    batch_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    status: Mapped[str] = mapped_column(
        String(30), default="PREPARED", index=True
    )  # PREPARED, PROCESSING, COMPLETED, FAILED
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_employees: Mapped[int] = mapped_column(Integer)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    reconciled_count: Mapped[int] = mapped_column(Integer, default=0)
    disbursed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    payroll_run: Mapped[PayrollRun] = relationship("PayrollRun", back_populates="disbursement_batches")
    records: Mapped[list[DisbursementRecord]] = relationship(
        "DisbursementRecord", back_populates="batch", cascade="all, delete-orphan"
    )


class DisbursementRecord(Base):
    __tablename__ = "disbursement_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("disbursement_batches.id", ondelete="CASCADE"), index=True
    )
    employee_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("employee_payroll_profiles.id"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    bank_name: Mapped[str] = mapped_column(String(100))
    bank_account_number: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="SUCCESS")  # SUCCESS, FAILED
    simulated_reference: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    error_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_retried_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reconciled: Mapped[bool] = mapped_column(Boolean, default=False)
    reconciled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    batch: Mapped[DisbursementBatch] = relationship("DisbursementBatch", back_populates="records")
    employee_profile: Mapped[EmployeePayrollProfile] = relationship("EmployeePayrollProfile")


class Payslip(Base):
    __tablename__ = "payslips"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payslip_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    payroll_run_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payroll_run_items.id"), index=True
    )
    employee_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("employee_payroll_profiles.id"), index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payroll_periods.id"), index=True
    )
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    net_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    issue_date: Mapped[date] = mapped_column(Date)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    run_item: Mapped[PayrollRunItem] = relationship("PayrollRunItem", back_populates="payslip")
    employee_profile: Mapped[EmployeePayrollProfile] = relationship("EmployeePayrollProfile", back_populates="payslips")
    period: Mapped[PayrollPeriod] = relationship("PayrollPeriod")


class PayrollAuditRecord(Base):
    __tablename__ = "payroll_audit_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource_type: Mapped[str] = mapped_column(String(60), index=True)
    resource_id: Mapped[str] = mapped_column(String(100), index=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class PayrollOutboxEvent(Base):
    __tablename__ = "payroll_outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    relay_attempts: Mapped[int] = mapped_column(Integer, default=0)
    relay_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    relay_error: Mapped[str | None] = mapped_column(String(240), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PayrollInboxEvent(Base):
    __tablename__ = "payroll_inbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    source_service: Mapped[str] = mapped_column(String(80))
    event_type: Mapped[str] = mapped_column(String(160))
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

