from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import EntityNotFoundError, PayrollDomainError
from app.domain.models import (
    DisbursementBatch,
    DisbursementRecord,
    EmployeePayrollProfile,
    PayrollAuditRecord,
    PayrollOutboxEvent,
    PayrollPeriod,
    PayrollRun,
    PayrollRunItem,
    Payslip,
    SalaryComponent,
    SalaryStructure,
)
from app.services.calculation_engine import PayrollCalculationEngine


class PayrollService:
    def __init__(self, db: Session):
        self.db = db

    # Profiles & Structures
    def create_employee_profile(
        self,
        *,
        user_id: uuid.UUID,
        employee_number: str,
        full_name: str,
        email: str,
        designation: str = "Faculty",
        employment_type: str = "FULL_TIME",
        department_id: uuid.UUID | None = None,
        bank_name: str = "Habib Bank Limited",
        bank_account_number: str = "1234567890",
        is_active: bool = True,
    ) -> EmployeePayrollProfile:
        existing = self.db.scalar(
            select(EmployeePayrollProfile).where(
                (EmployeePayrollProfile.user_id == user_id)
                | (EmployeePayrollProfile.employee_number == employee_number)
            )
        )
        if existing:
            raise PayrollDomainError(f"Employee profile already exists with number {employee_number} or user {user_id}")

        profile = EmployeePayrollProfile(
            user_id=user_id,
            employee_number=employee_number,
            full_name=full_name,
            email=email,
            department_id=department_id,
            designation=designation,
            employment_type=employment_type.upper(),
            bank_name=bank_name,
            bank_account_number=bank_account_number,
            is_active=is_active,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def assign_salary_structure(
        self,
        *,
        employee_profile_id: uuid.UUID,
        effective_from: date,
        base_salary: Decimal,
        components_data: list[dict[str, Any]],
        effective_to: date | None = None,
    ) -> SalaryStructure:
        profile = self.db.get(EmployeePayrollProfile, employee_profile_id)
        if not profile:
            raise EntityNotFoundError(f"Employee profile {employee_profile_id} not found")

        # Deactivate previous active structures
        previous = self.db.scalars(
            select(SalaryStructure).where(
                SalaryStructure.employee_profile_id == employee_profile_id,
                SalaryStructure.is_active == True,
            )
        ).all()
        version = len(previous) + 1
        for s in previous:
            s.is_active = False

        structure = SalaryStructure(
            employee_profile_id=employee_profile_id,
            effective_from=effective_from,
            effective_to=effective_to,
            base_salary=base_salary,
            version=version,
            is_active=True,
        )
        self.db.add(structure)
        self.db.flush()

        for c_data in components_data:
            c = SalaryComponent(
                salary_structure_id=structure.id,
                name=c_data["name"],
                component_type=c_data.get("component_type", "ALLOWANCE").upper(),
                amount=Decimal(str(c_data["amount"])).quantize(Decimal("0.01")),
                is_percentage=c_data.get("is_percentage", False),
                percentage_value=Decimal(str(c_data["percentage_value"])) if c_data.get("percentage_value") else None,
            )
            self.db.add(c)

        self.db.commit()
        self.db.refresh(structure)
        return structure

    # Periods
    def create_period(self, year: int, month: int, start_date: date, end_date: date) -> PayrollPeriod:
        existing = self.db.scalar(
            select(PayrollPeriod).where(PayrollPeriod.year == year, PayrollPeriod.month == month)
        )
        if existing:
            return existing

        period = PayrollPeriod(year=year, month=month, start_date=start_date, end_date=end_date, status="OPEN")
        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)
        return period

    # Runs & Calculations
    def calculate_payroll_run(
        self,
        *,
        period_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        notes: str | None = None,
    ) -> PayrollRun:
        period = self.db.get(PayrollPeriod, period_id)
        if not period:
            raise EntityNotFoundError(f"Payroll period {period_id} not found")

        # Period uniqueness check: only one active or finalized run per period
        existing = self.db.scalar(
            select(PayrollRun).where(
                PayrollRun.period_id == period_id,
                PayrollRun.status.in_({"CALCULATED", "APPROVED", "DISBURSEMENT_PENDING", "PAID"}),
            )
        )
        if existing:
            raise PayrollDomainError(
                f"A payroll run ({existing.run_number}) already exists for this period with status {existing.status}"
            )

        profiles = self.db.scalars(
            select(EmployeePayrollProfile).where(EmployeePayrollProfile.is_active == True)
        ).all()
        if not profiles:
            raise PayrollDomainError("No active employee profiles available for payroll calculation")

        run_no = f"PAY-{period.year}{period.month:02d}-{uuid.uuid4().hex[:6].upper()}"
        run = PayrollRun(
            period_id=period_id,
            run_number=run_no,
            status="CALCULATED",
            total_gross=Decimal("0.00"),
            total_deductions=Decimal("0.00"),
            total_net=Decimal("0.00"),
            created_by_user_id=created_by_user_id,
            notes=notes,
        )
        self.db.add(run)
        self.db.flush()

        grand_gross = Decimal("0.00")
        grand_deductions = Decimal("0.00")
        grand_net = Decimal("0.00")

        for p in profiles:
            active_structure = self.db.scalar(
                select(SalaryStructure).where(
                    SalaryStructure.employee_profile_id == p.id,
                    SalaryStructure.is_active == True,
                )
            )
            if not active_structure:
                continue

            calc = PayrollCalculationEngine.calculate_employee_payroll(active_structure, days_worked=30)
            item = PayrollRunItem(
                payroll_run_id=run.id,
                employee_profile_id=p.id,
                base_salary=calc["base_salary"],
                total_allowances=calc["total_allowances"],
                total_deductions=calc["total_deductions"],
                gross_salary=calc["gross_salary"],
                net_salary=calc["net_salary"],
                days_worked=calc["days_worked"],
                proration_factor=calc["proration_factor"],
                details=calc["details"],
            )
            self.db.add(item)
            grand_gross += calc["gross_salary"]
            grand_deductions += calc["total_deductions"]
            grand_net += calc["net_salary"]

        run.total_gross = grand_gross
        run.total_deductions = grand_deductions
        run.total_net = grand_net

        # Audit record
        self.db.add(
            PayrollAuditRecord(
                actor_id=created_by_user_id,
                action="PAYROLL_CALCULATED",
                resource_type="PAYROLL_RUN",
                resource_id=str(run.id),
                details={"run_number": run.run_number, "total_net": str(run.total_net)},
            )
        )

        self.db.commit()
        self.db.refresh(run)
        return run

    def approve_payroll_run(
        self,
        *,
        run_id: uuid.UUID,
        approved_by_user_id: uuid.UUID,
        approved: bool,
        notes: str | None = None,
    ) -> PayrollRun:
        run = self.db.scalar(select(PayrollRun).where(PayrollRun.id == run_id).with_for_update())
        if not run or run.status != "CALCULATED":
            raise PayrollDomainError("Payroll run is not in a CALCULATED state pending approval")

        # Strict Maker-Checker Invariant: creator cannot approve their own run
        if run.created_by_user_id == approved_by_user_id:
            raise PayrollDomainError(
                "Maker-checker violation: An operator cannot approve a payroll run they created"
            )

        run.approved_by_user_id = approved_by_user_id
        if not approved:
            run.status = "REJECTED"
            run.notes = notes or "Rejected during review"
            self.db.commit()
            return run

        now = datetime.now(UTC)
        run.status = "APPROVED"
        run.approved_at = now
        run.notes = notes

        # Generate published payslips for all run items
        items = self.db.scalars(
            select(PayrollRunItem).where(PayrollRunItem.payroll_run_id == run.id)
        ).all()
        for item in items:
            payslip_no = f"SLIP-{now.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
            slip = Payslip(
                payslip_number=payslip_no,
                payroll_run_item_id=item.id,
                employee_profile_id=item.employee_profile_id,
                period_id=run.period_id,
                gross_salary=item.gross_salary,
                net_salary=item.net_salary,
                breakdown=item.details,
                issue_date=now.date(),
                is_published=True,
            )
            self.db.add(slip)

        # Outbox event
        self.db.add(
            PayrollOutboxEvent(
                aggregate_id=run.id,
                event_type="payroll.run.approved.v1",
                payload={
                    "payroll_run_id": str(run.id),
                    "run_number": run.run_number,
                    "total_net": str(run.total_net),
                    "approved_at": now.isoformat(),
                },
            )
        )

        # Audit record
        self.db.add(
            PayrollAuditRecord(
                actor_id=approved_by_user_id,
                action="PAYROLL_APPROVED",
                resource_type="PAYROLL_RUN",
                resource_id=str(run.id),
                details={"approved": True, "items_count": len(items)},
            )
        )

        self.db.commit()
        self.db.refresh(run)
        return run

    def execute_disbursements(
        self,
        *,
        run_id: uuid.UUID,
        actor_id: uuid.UUID | None = None,
    ) -> DisbursementBatch:
        run = self.db.scalar(select(PayrollRun).where(PayrollRun.id == run_id).with_for_update())
        if not run or run.status != "APPROVED":
            raise PayrollDomainError("Only APPROVED payroll runs can be disbursed")

        now = datetime.now(UTC)
        items = self.db.scalars(
            select(PayrollRunItem).where(PayrollRunItem.payroll_run_id == run.id)
        ).all()

        batch_no = f"DISB-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        batch = DisbursementBatch(
            payroll_run_id=run.id,
            batch_number=batch_no,
            status="COMPLETED",
            total_amount=run.total_net,
            total_employees=len(items),
            disbursed_at=now,
        )
        self.db.add(batch)
        self.db.flush()

        for item in items:
            profile = item.employee_profile
            sim_ref = f"SIM-PAYOUT-{uuid.uuid4().hex[:12].upper()}"
            rec = DisbursementRecord(
                batch_id=batch.id,
                employee_profile_id=profile.id,
                amount=item.net_salary,
                bank_name=profile.bank_name,
                bank_account_number=profile.bank_account_number,
                status="SUCCESS",
                simulated_reference=sim_ref,
            )
            self.db.add(rec)

        run.status = "PAID"

        # Outbox event
        self.db.add(
            PayrollOutboxEvent(
                aggregate_id=batch.id,
                event_type="payroll.disbursement.completed.v1",
                payload={
                    "batch_id": str(batch.id),
                    "batch_number": batch_no,
                    "payroll_run_id": str(run.id),
                    "total_amount": str(batch.total_amount),
                },
            )
        )

        self.db.commit()
        self.db.refresh(batch)
        return batch

