import logging
import os
import sys
from datetime import datetime

from .api import *
from .data import *
from .embeddings import *
from .services import *
from .sources import *
from .config import *


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


init_logging()
