import argparse
import logging

from firstlight.pipeline.run import run_pipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main():
    parser = argparse.ArgumentParser(description="First Light CLI")
    parser.add_argument("command", choices=["run", "init-db", "web"])
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without sending or AI calls"
    )
    parser.add_argument(
        "--no-ai", action="store_true", help="Force fallback mode without AI"
    )

    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(dry_run=args.dry_run, no_ai=args.no_ai)
    elif args.command == "init-db":
        from firstlight.db import init_db

        init_db()
    elif args.command == "web":
        from firstlight.web.app import create_app

        app = create_app()
        app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
