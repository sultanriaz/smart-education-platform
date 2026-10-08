from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.domain.entities.models import LearningResource, ResourceTarget, ResourceType, TargetType


@pytest.mark.skipif(not os.getenv("TEST_POSTGRES_URL"), reason="TEST_POSTGRES_URL not configured")
def test_postgres_rejects_duplicate_resource_target():
    engine = create_engine(os.environ["TEST_POSTGRES_URL"])
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    db = Session()
    try:
        resource = LearningResource(
            title="Concurrency Target",
            resource_type=ResourceType.NOTE,
            creator_user_id=uuid.uuid4(),
        )
        db.add(resource)
        db.flush()
        target_id = uuid.uuid4()
        db.add_all(
            [
                ResourceTarget(
                    resource_id=resource.id, target_type=TargetType.SECTION, target_id=target_id
                ),
                ResourceTarget(
                    resource_id=resource.id, target_type=TargetType.SECTION, target_id=target_id
                ),
            ]
        )
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(engine)
