import logging
import sys
import os
from datetime import datetime

from semantic_index import config, Manager, FileSourceHandler


def init_logging():
    os.makedirs(config.log_folder, exist_ok=True)

    log_filename = os.path.join(
        config.log_folder, f"log_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    )

    file_handler = logging.FileHandler(log_filename)
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

    manager: Manager = Manager()

    fh = FileSourceHandler()
    manager.resolver.register(fh)

    # manager.index.recreate_db()
    # manager.index.ingest_sources(
    #     fh.crawl(r"C:\Users\twuerth\OneDrive - insite ag\Desktop\docs")
    # )
    # manager.process_sources()
    # manager.index.reload_data()

    manager.find_knn("EO", 5)
