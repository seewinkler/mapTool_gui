import logging
import os

def setup_logging(loglevel=logging.DEBUG, logfile="maptool.log"):
    logpath = os.path.join(os.path.dirname(__file__), "..", logfile)
    logpath = os.path.normpath(logpath)

    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(logpath, encoding='utf-8'),
            logging.StreamHandler()  # Optional: zeigt Logs auch im Terminal
        ]
    )