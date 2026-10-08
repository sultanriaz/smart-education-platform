from app.main import app


def test_app_title():
    assert "Assessment" in app.title
