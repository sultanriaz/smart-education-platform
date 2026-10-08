from __future__ import annotations

import uuid

from app.schemas.admin import FeatureFlagUpsert, JobCreate, SettingUpsert


def test_setting_upsert(platform):
    admin = uuid.uuid4()
    row = platform.upsert_setting(
        "campus.branding",
        SettingUpsert(
            value={"name": "Smart Education"},
            is_public=True,
            description="Public branding",
        ),
        admin,
    )
    assert row.is_public is True
    assert row.value["name"] == "Smart Education"

    updated = platform.upsert_setting(
        "campus.branding",
        SettingUpsert(value={"name": "Smart Campus"}, is_public=True),
        admin,
    )
    assert updated.value["name"] == "Smart Campus"
    assert len(platform.repo.list_settings()) == 1


def test_feature_flag_upsert(platform):
    admin = uuid.uuid4()
    feature = platform.upsert_feature(
        "assessment.experimental-ui",
        FeatureFlagUpsert(enabled=True, config={"percentage": 25}),
        admin,
    )
    assert feature.enabled is True
    assert feature.config["percentage"] == 25


def test_job_creation(platform):
    admin = uuid.uuid4()
    job = platform.create_job(
        JobCreate(
            job_type="EXPORT",
            target_service="academic-service",
            resource_type="students",
            parameters={"semester": "fall-2026"},
        ),
        admin,
    )
    assert job.status == "QUEUED"
    assert job.target_service == "academic-service"
    assert len(platform.repo.list_jobs()) == 1
