"""Normalize only the obsolete fixture created by this integration run."""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.domain.entities.user import User


def main():
    # Never run against a user-selected or production connection.
    from sqlalchemy.engine import make_url

    from app.core.config import settings

    url = make_url(settings.DATABASE_URL)
    if settings.ENVIRONMENT != "development" or url.host != "127.0.0.1" or url.port != 55432:
        raise SystemExit("Local demo repair only supports the isolated integration database.")
    with SessionLocal() as db:
        old = db.scalar(
            select(User).where(
                User.email == "admin@demo.smartedu.test", User.full_name == "Demo Administrator"
            )
        )
        if old:
            old.email = "obsolete-admin@demo.example.edu"
            old.is_active = False
            db.commit()
            print("Normalized obsolete local fixture; account/history preserved.")


if __name__ == "__main__":
    main()
