import argparse
import logging
import sys

from semantic_index import get_manager, Manager, SearchDateFilter


def init_parser():
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
        "--search",
        "-s",
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
    return parser


def handle_ingest(manager: Manager, args: argparse.Namespace):
    if not args.ingest:
        return

    # check handler
    handler_name, source_path = args.ingest
    logging.info(f"Ingesting {source_path} using handler '{handler_name}'")
    handler = manager.resolver.get_handler_by_name(handler_name)
    if handler is None:
        logging.error(f"Handler '{handler_name}' not registered")
        sys.exit(1)

    sources = handler.crawl(source_path)
    manager.processing_service.ingest_sources(sources)
    logging.info(f"Ingested sources from {source_path}")
    logging.info("-" * 40)


def handle_process(manager: Manager, args: argparse.Namespace):
    if not args.process:
        return

    logging.info("Processing all sources")
    manager.processing_service.process_pending_sources()
    logging.info("Processed all sources")
    logging.info("-" * 40)


def handle_search(manager: Manager, args: argparse.Namespace):
    if not args.search:
        return

    logging.info(f"Finding KNN for query: {args.search} with k={args.kcount}")
    full_range_filter = SearchDateFilter(
        createdate_start=None,
        createdate_end=None,
        modifieddate_start=None,
        modifieddate_end=None,
    )
    results = manager.search_service.search_documents(
        args.search, full_range_filter, k=args.kcount
    )
    logging.info(f"Top {args.kcount} results for: '{args.search}'")
    for result in results:
        logging.info(
            f" > ID {result.source.id} similarity {result.similarity:.4f}: {result.source.uri}"
        )


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()
    if not (args.ingest or args.process or args.search):
        logging.error(parser.format_help())
        sys.exit(1)

    manager = get_manager()
    handle_ingest(manager, args)
    handle_process(manager, args)
    handle_search(manager, args)

    logging.info("Semantic Index Manager exiting.")
