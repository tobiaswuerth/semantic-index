import logging
import sys
import os
from datetime import datetime
import argparse

from semantic_index import config, Manager, FileSourceHandler


def init_logging():
    os.makedirs(config.log_folder, exist_ok=True)

    log_filename = os.path.join(
        config.log_folder, f"log_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    )

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(getattr(logging, config.log_level_file))

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(getattr(logging, config.log_level_console))

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [ %(levelname)s ] %(message)s",
        handlers=[file_handler, stream_handler],
    )


if __name__ == "__main__":
    init_logging()

    parser = argparse.ArgumentParser(description="Semantic Index Manager")

    parser.add_argument(
        "--ingest",
        "-i",
        metavar="PATH",
        help="Ingest sources from the specified path",
    )

    parser.add_argument(
        "--process",
        "-p",
        action="store_true",
        help="Process all sources",
    )

    parser.add_argument(
        "--knn",
        "-k",
        metavar="QUERY",
        help="Find k-nearest neighbors for the query",
    )

    parser.add_argument(
        "--kcount",
        "-kc",
        type=int,
        default=5,
        help="Number of results to return for KNN search (default: 5)",
    )

    args = parser.parse_args()
    if not (args.ingest or args.process or args.knn):
        logging.error(parser.format_help())
        sys.exit(1)

    logging.info("Starting Semantic Index Manager...")
    manager = Manager()
    fh = FileSourceHandler()
    manager.resolver.register(fh)
    logging.info("Initialized Semantic Index Manager")
    logging.info("-" * 40)

    if args.ingest:
        logging.info(f"Ingesting sources from: {args.ingest}")
        sources = fh.crawl(args.ingest)
        manager.index.ingest_sources(sources)
        manager.index.reload_data()
        logging.info(f"Ingested sources from {args.ingest}")
        logging.info("-" * 40)

    if args.process:
        logging.info("Processing all sources")
        manager.process_sources()
        logging.info("Processed all sources")
        logging.info("-" * 40)

    if args.knn:
        logging.info(f"Finding KNN for query: {args.knn} with k={args.kcount}")
        results = manager.find_knn(args.knn, k=args.kcount)
        logging.info(f"Top {args.kcount} results for: '{args.knn}'")
        for i, result in enumerate(results, start=1):
            s = result["source"]
            logging.info(
                f' > ID {s["id"]} similarity {result['similarity']:.4f}: {s["uri"]}'
            )
