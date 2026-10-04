import argparse
import logging

from firstlight.pipeline.run import run_pipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main():
    parser = argparse.ArgumentParser(description="First Light CLI")
    parser.add_argument("command", choices=["run"])
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without sending or AI calls"
    )

    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
