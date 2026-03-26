import sys
import time
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

BACKEND_APP_PATH = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_APP_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_PATH))

from app.db.session import SessionLocal
from app.services.parse_jobs import load_next_pending_parse_job, process_parse_job


POLL_INTERVAL_SECONDS = 3
DB_RETRY_INTERVAL_SECONDS = 10


def main() -> None:
    print("[worker] StarGraph AI worker started")
    processed = 0
    while True:
        db = SessionLocal()
        try:
            job = load_next_pending_parse_job(db)
        except SQLAlchemyError as exc:
            print(
                f"[worker] Database unavailable, retrying in {DB_RETRY_INTERVAL_SECONDS}s: {exc}"
            )
            time.sleep(DB_RETRY_INTERVAL_SECONDS)
            continue
        finally:
            db.close()

        if job is None:
            print("[worker] No pending parse job found")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        print(f"[worker] Processing job: {job.id}")
        process_parse_job(db, job)
        processed += 1
        print(f"[worker] Total processed: {processed}")

        time.sleep(0.2)


if __name__ == "__main__":
    main()
