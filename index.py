import argparse
import logging
import os
import sys
from datetime import datetime

from semantic_index import Manager, config


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
        nargs=2,
        metavar=("HANDLER", "SOURCE"),
        help="Ingest sources using the specified handler and source (e.g., -i file /path/to/folder, -i jira https://my.url/api)",
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

    parser.add_argument(
        "--arg",
        "-a",
        action="append",
        metavar="KEY=VALUE",
        default=[],
        help="Handler-specific arguments as key=value pairs (can be used multiple times, e.g., -a key=my_api_key -a project=MYPROJ)",
    )

    args = parser.parse_args()
    if not (args.ingest or args.process or args.knn):
        logging.error(parser.format_help())
        sys.exit(1)

    logging.info("Starting Semantic Index Manager...")
    manager = Manager()
    logging.info("Initialized Semantic Index Manager")
    logging.info("-" * 40)

    if args.ingest:
        handler_name, source_path = args.ingest
        logging.info(f"Ingesting sources using handler '{handler_name}' from: {source_path}")
        handler = manager.get_handler(handler_name)
        if handler is None:
            logging.error(f"Handler '{handler_name}' not registered")
            sys.exit(1)

        # Parse handler-specific arguments
        handler_args = {}
        for arg in args.arg:
            if "=" not in arg:
                logging.error(f"Invalid argument format: '{arg}'. Expected KEY=VALUE")
                sys.exit(1)
            key, value = arg.split("=", 1)
            handler_args[key] = value

        sources = handler.crawl(source_path, **handler_args)
        manager.ingest_sources(sources)
        logging.info(f"Ingested sources from {source_path}")
        logging.info("-" * 40)

    if args.process:
        logging.info("Processing all sources")
        manager.process_sources()
        logging.info("Processed all sources")
        logging.info("-" * 40)

    if args.knn:
        logging.info(f"Finding KNN for query: {args.knn} with k={args.kcount}")
        results = manager.find_knn_chunks(args.knn, k=args.kcount)
        logging.info(f"Top {args.kcount} results for: '{args.knn}'")
        for i, result in enumerate(results, start=1):
            logging.info(
                f" > ID {result.source.id} similarity {result.similarity:.4f}: {result.source.uri}"
            )
