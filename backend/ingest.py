import argparse
import logging
import sys
from pathlib import Path

from ingestion.pipeline import IngestionPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into vector store.")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Path to documents folder (default: config DOCS_DIR)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing vector store before ingestion",
    )
    args = parser.parse_args()

    pipeline = IngestionPipeline()
    result = pipeline.run(docs_dir=args.docs_dir, clear_existing=args.clear)

    if result["status"] == "success":
        print(f"\nDone! {result['documents_loaded']} docs → "
              f"{result['chunks_created']} chunks stored.")
    else:
        print(f"\nIngestion skipped: {result.get('reason')}")
        sys.exit(1)


if __name__ == "__main__":
    main()