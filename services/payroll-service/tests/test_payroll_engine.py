from decimal import Decimal
import pytest
from app.services.calculation_engine import PayrollCalculationEngine
from app.domain.models import SalaryStructure, SalaryComponent

class MockStructure:
    def __init__(self, base_salary, components):
        self.base_salary = Decimal(str(base_salary))
        self.components = components

class MockComponent:
    def __init__(self, name, component_type, amount, is_percentage=False, percentage_value=None):
        self.name = name
        self.component_type = component_type
        self.amount = Decimal(str(amount))
        self.is_percentage = is_percentage
        self.percentage_value = Decimal(str(percentage_value)) if percentage_value else None

def test_gross_to_net_calculation():
    components = [
        MockComponent("House Rent Allowance", "ALLOWANCE", 15000),
        MockComponent("Medical Allowance", "ALLOWANCE", 5000),
        MockComponent("Income Tax", "DEDUCTION", 8000),
        MockComponent("Provident Fund", "DEDUCTION", 4000),
    ]
    structure = MockStructure(base_salary=120000, components=components)

    result = PayrollCalculationEngine.calculate_employee_payroll(structure, days_worked=30, total_working_days=30)

    assert result["base_salary"] == Decimal("120000.00")
    assert result["total_allowances"] == Decimal("20000.00")
    assert result["gross_salary"] == Decimal("140000.00")
    assert result["total_deductions"] == Decimal("12000.00")
    assert result["net_salary"] == Decimal("128000.00")
    assert result["proration_factor"] == Decimal("1.00")

def test_prorated_salary_calculation():
    components = [
        MockComponent("Allowance", "ALLOWANCE", 10000),
        MockComponent("Deduction", "DEDUCTION", 5000),
    ]
    structure = MockStructure(base_salary=100000, components=components)

    # Worked 15 days out of 30 (50% proration)
    result = PayrollCalculationEngine.calculate_employee_payroll(structure, days_worked=15, total_working_days=30)

    assert result["days_worked"] == 15
    assert result["proration_factor"] == Decimal("0.500000")
    assert result["base_salary"] == Decimal("50000.00")
    assert result["total_allowances"] == Decimal("5000.00")
    assert result["gross_salary"] == Decimal("55000.00")
    assert result["total_deductions"] == Decimal("2500.00")
    assert result["net_salary"] == Decimal("52500.00")

