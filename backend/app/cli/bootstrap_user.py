import argparse
import getpass

from pydantic import ValidationError

from app.core.database import SessionLocal
from app.schemas.auth import LoginRequest
from app.services.auth import AuthService, BootstrapError


def main() -> int:
    parser = argparse.ArgumentParser(description="Create credentials for an empty or single legacy health-app user.")
    parser.add_argument("--email", required=True, help="Email address for the local account")
    args = parser.parse_args()
    try:
        email = LoginRequest(email=args.email, password="placeholder").email
    except ValidationError:
        print("A valid email address is required.")
        return 2
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        print("Passwords do not match.")
        return 2
    db = SessionLocal()
    try:
        user = AuthService.bootstrap_single_user(db, email, password)
    except BootstrapError as error:
        print(str(error))
        return 1
    finally:
        db.close()
    print(f"Credentials configured for user {user.id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
