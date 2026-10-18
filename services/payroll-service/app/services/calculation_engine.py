from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.domain.models import SalaryStructure


class PayrollCalculationEngine:
    @staticmethod
    def calculate_employee_payroll(
        structure: SalaryStructure,
        days_worked: int = 30,
        total_working_days: int = 30,
    ) -> dict[str, Any]:
        """Compute base salary, allowances, deductions, gross, and net pay.
        
        Example from Section 4:
        Base: PKR 120,000
        Allowances: PKR 10,000
        Deduction: PKR 5,000
        Gross: PKR 130,000
        Net: PKR 125,000
        """
        base = structure.base_salary
        safe_days = max(1, min(days_worked, total_working_days))
        proration = (Decimal(str(safe_days)) / Decimal(str(total_working_days))).quantize(Decimal("0.0001"))
        prorated_base = (base * proration).quantize(Decimal("0.01"))

        allowances_breakdown = []
        deductions_breakdown = []
        total_allowances = Decimal("0.00")
        total_deductions = Decimal("0.00")

        for comp in structure.components:
            if comp.is_percentage and comp.percentage_value:
                comp_val = (prorated_base * (comp.percentage_value / Decimal("100.00"))).quantize(Decimal("0.01"))
            else:
                comp_val = (comp.amount * proration).quantize(Decimal("0.01"))

            item = {
                "name": comp.name,
                "amount": str(comp_val),
                "is_percentage": comp.is_percentage,
                "percentage_value": str(comp.percentage_value) if comp.percentage_value else None,
            }

            if comp.component_type.upper() == "ALLOWANCE":
                total_allowances += comp_val
                allowances_breakdown.append(item)
            else:
                total_deductions += comp_val
                deductions_breakdown.append(item)

        gross = (prorated_base + total_allowances).quantize(Decimal("0.01"))
        net = max(Decimal("0.00"), gross - total_deductions).quantize(Decimal("0.01"))

        return {
            "base_salary": prorated_base,
            "total_allowances": total_allowances,
            "total_deductions": total_deductions,
            "gross_salary": gross,
            "net_salary": net,
            "days_worked": safe_days,
            "proration_factor": proration,
            "details": {
                "contract_base_salary": str(base),
                "allowances": allowances_breakdown,
                "deductions": deductions_breakdown,
            },
        }

