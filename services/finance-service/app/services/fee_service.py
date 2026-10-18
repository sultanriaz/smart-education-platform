from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import EntityNotFoundError, FinanceDomainError
from app.domain.models import FeeComponent, FeeStructure, Scholarship, ScholarshipAward


class FeeService:
    def __init__(self, db: Session):
        self.db = db

    def create_fee_structure(
        self,
        *,
        name: str,
        program_id: uuid.UUID,
        academic_year_id: uuid.UUID,
        semester_number: int,
        components_data: list[dict[str, Any]],
        is_active: bool = True,
    ) -> FeeStructure:
        if not components_data:
            raise FinanceDomainError("Fee structure must contain at least one fee component")

        structure = FeeStructure(
            name=name,
            program_id=program_id,
            academic_year_id=academic_year_id,
            semester_number=semester_number,
            is_active=is_active,
        )
        self.db.add(structure)
        self.db.flush()

        for comp in components_data:
            amount = Decimal(str(comp["amount"])).quantize(Decimal("0.01"))
            if amount <= Decimal("0.00"):
                raise FinanceDomainError(f"Component amount must be positive: {comp.get('name')}")
            c = FeeComponent(
                fee_structure_id=structure.id,
                name=comp["name"],
                component_type=comp.get("component_type", "TUITION").upper(),
                amount=amount,
                is_refundable=comp.get("is_refundable", False),
                eligible_for_scholarship=comp.get("eligible_for_scholarship", True),
            )
            self.db.add(c)

        self.db.commit()
        self.db.refresh(structure)
        return structure

    def get_fee_structure(self, structure_id: uuid.UUID) -> FeeStructure:
        structure = self.db.get(FeeStructure, structure_id)
        if structure is None:
            raise EntityNotFoundError(f"Fee structure {structure_id} not found")
        return structure

    def find_fee_structure(
        self,
        program_id: uuid.UUID,
        academic_year_id: uuid.UUID,
        semester_number: int,
    ) -> FeeStructure | None:
        query = (
            select(FeeStructure)
            .where(
                FeeStructure.program_id == program_id,
                FeeStructure.academic_year_id == academic_year_id,
                FeeStructure.semester_number == semester_number,
                FeeStructure.is_active == True,
            )
            .order_by(FeeStructure.created_at.desc())
        )
        return self.db.scalars(query).first()

    def list_fee_structures(
        self,
        program_id: uuid.UUID | None = None,
        academic_year_id: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> list[FeeStructure]:
        query = select(FeeStructure).order_by(FeeStructure.created_at.desc())
        if program_id is not None:
            query = query.where(FeeStructure.program_id == program_id)
        if academic_year_id is not None:
            query = query.where(FeeStructure.academic_year_id == academic_year_id)
        if is_active is not None:
            query = query.where(FeeStructure.is_active == is_active)
        return list(self.db.scalars(query).all())

    # Scholarship configurations
    def create_scholarship(
        self,
        *,
        name: str,
        code: str,
        scholarship_type: str,
        percentage: Decimal,
        applies_to_components: list[str] | None = None,
    ) -> Scholarship:
        pct = Decimal(str(percentage)).quantize(Decimal("0.01"))
        if pct <= 0 or pct > 100:
            raise FinanceDomainError("Scholarship percentage must be between 0.01 and 100.00")

        existing = self.db.scalar(select(Scholarship).where(Scholarship.code == code.upper()))
        if existing:
            raise FinanceDomainError(f"Scholarship with code {code} already exists")

        applies = applies_to_components or ["TUITION"]
        s = Scholarship(
            name=name,
            code=code.upper(),
            scholarship_type=scholarship_type.upper(),
            percentage=pct,
            applies_to_components=[c.upper() for c in applies],
            is_active=True,
        )
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return s

    def award_scholarship(
        self,
        *,
        scholarship_id: uuid.UUID,
        student_user_id: uuid.UUID,
        academic_year_id: uuid.UUID,
        semester_number: int,
        granted_by_user_id: uuid.UUID,
    ) -> ScholarshipAward:
        scholarship = self.db.get(Scholarship, scholarship_id)
        if not scholarship or not scholarship.is_active:
            raise FinanceDomainError("Active scholarship policy not found")

        award = ScholarshipAward(
            scholarship_id=scholarship_id,
            student_user_id=student_user_id,
            academic_year_id=academic_year_id,
            semester_number=semester_number,
            status="ACTIVE",
            granted_by_user_id=granted_by_user_id,
        )
        self.db.add(award)
        self.db.commit()
        self.db.refresh(award)
        return award

    def calculate_concession(
        self,
        student_user_id: uuid.UUID,
        academic_year_id: uuid.UUID,
        semester_number: int,
        components: list[FeeComponent],
    ) -> tuple[Decimal, dict[str, Decimal]]:
        """Calculate total scholarship discount and per-component discounts."""
        awards = self.db.scalars(
            select(ScholarshipAward)
            .where(
                ScholarshipAward.student_user_id == student_user_id,
                ScholarshipAward.academic_year_id == academic_year_id,
                ScholarshipAward.semester_number == semester_number,
                ScholarshipAward.status == "ACTIVE",
            )
        ).all()

        if not awards:
            return Decimal("0.00"), {}

        # Max percentage among active awards (or composite rules)
        best_award = max(awards, key=lambda a: a.scholarship.percentage)
        pct = best_award.scholarship.percentage / Decimal("100.00")
        applies_to = {c.upper() for c in (best_award.scholarship.applies_to_components or ["TUITION"])}

        total_concession = Decimal("0.00")
        component_discounts = {}

        for comp in components:
            if comp.eligible_for_scholarship and comp.component_type.upper() in applies_to:
                discount = (comp.amount * pct).quantize(Decimal("0.01"))
                component_discounts[comp.name] = discount
                total_concession += discount
            else:
                component_discounts[comp.name] = Decimal("0.00")

        return total_concession, component_discounts

