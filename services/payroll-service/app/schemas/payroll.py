from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Profiles
class SalaryComponentIn(BaseModel):
    name: str
    component_type: str = "ALLOWANCE"  # ALLOWANCE, DEDUCTION
    amount: Decimal
    is_percentage: bool = False
    percentage_value: Decimal | None = None


class SalaryComponentOut(SalaryComponentIn):
    id: uuid.UUID
    salary_structure_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class SalaryStructureIn(BaseModel):
    employee_profile_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None
    base_salary: Decimal
    components: list[SalaryComponentIn] = Field(default_factory=list)


class SalaryStructureOut(BaseModel):
    id: uuid.UUID
    employee_profile_id: uuid.UUID
    effective_from: date
    effective_to: date | None = None
    base_salary: Decimal
    version: int
    is_active: bool
    created_at: datetime
    components: list[SalaryComponentOut] = Field(default_factory=list)
    name: str = "Faculty Salary Structure"

    model_config = ConfigDict(from_attributes=True)


class EmployeePayrollProfileIn(BaseModel):
    user_id: uuid.UUID
    employee_number: str
    full_name: str
    email: str
    department_id: uuid.UUID | None = None
    designation: str = "Faculty"
    employment_type: str = "FULL_TIME"  # FULL_TIME, PART_TIME, CONTRACT
    bank_name: str = "Habib Bank Limited"
    bank_account_number: str
    is_active: bool = True


class EmployeePayrollProfileOut(EmployeePayrollProfileIn):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    salary_structures: list[SalaryStructureOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Periods
class PayrollPeriodIn(BaseModel):
    year: int
    month: int
    start_date: date
    end_date: date


class PayrollPeriodOut(PayrollPeriodIn):
    id: uuid.UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Runs & Items
class PayrollRunCreateIn(BaseModel):
    period_id: uuid.UUID
    notes: str | None = None


class PayrollApprovalIn(BaseModel):
    approved: bool
    notes: str | None = None


class PayrollRunItemOut(BaseModel):
    id: uuid.UUID
    employee_profile_id: uuid.UUID
    base_salary: Decimal
    total_allowances: Decimal
    total_deductions: Decimal
    gross_salary: Decimal
    net_salary: Decimal
    days_worked: int
    proration_factor: Decimal
    details: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PayrollRunOut(BaseModel):
    id: uuid.UUID
    period_id: uuid.UUID
    run_number: str
    status: str
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    created_by_user_id: uuid.UUID
    approved_by_user_id: uuid.UUID | None = None
    approved_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[PayrollRunItemOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Disbursements
class DisburseRunIn(BaseModel):
    simulate_failures: bool = False
    fail_employee_ids: list[uuid.UUID] = Field(default_factory=list)


class DisbursementRecordOut(BaseModel):
    id: uuid.UUID
    employee_profile_id: uuid.UUID
    amount: Decimal
    bank_name: str
    bank_account_number: str
    status: str
    simulated_reference: str
    error_message: str | None = None
    retry_count: int = 0
    last_retried_at: datetime | None = None
    reconciled: bool = False
    reconciled_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DisbursementBatchOut(BaseModel):
    id: uuid.UUID
    payroll_run_id: uuid.UUID
    batch_number: str
    status: str
    total_amount: Decimal
    total_employees: int
    failed_count: int = 0
    reconciled_count: int = 0
    disbursed_at: datetime | None = None
    created_at: datetime
    records: list[DisbursementRecordOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DisbursementRetryIn(BaseModel):
    corrected_bank_name: str | None = None
    corrected_account_number: str | None = None


class BatchReconciliationOut(BaseModel):
    batch_id: uuid.UUID
    batch_number: str
    total_records: int
    reconciled_count: int
    failed_count: int
    status: str
    total_reconciled_amount: Decimal


# Payslips
class PayslipOut(BaseModel):
    id: uuid.UUID
    payslip_number: str
    payroll_run_item_id: uuid.UUID
    employee_profile_id: uuid.UUID
    period_id: uuid.UUID
    gross_salary: Decimal
    net_salary: Decimal
    breakdown: dict[str, Any]
    issue_date: date
    is_published: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

