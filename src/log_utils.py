# logger_config.py
import logging

import colorama
from colorama import Fore, Style
from scrapy.utils.log import configure_logging

# Initialize colorama
colorama.init(autoreset=True)


# Custom formatter for colored logs
class CustomFormatter(logging.Formatter):
    """Custom Formatter to add colors to log levels."""

    def format(self, record):
        log_colors = {
            logging.DEBUG: Fore.GREEN,
            logging.INFO: Fore.CYAN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.RED + Style.BRIGHT,
        }

        color = log_colors.get(record.levelno, Fore.WHITE)
        log_time = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        log_level = record.levelname
        log_message = record.msg

        record.msg = f"{color}{log_time} [{log_level}] {log_message}{Style.RESET_ALL}"

        return super().format(record)


# Configure logging
def configure_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    logging.basicConfig(
        level=logging.DEBUG,  # Set log level to DEBUG
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[handler],
    )

    # Set Scrapy logging level to INFO
    configure_logging(install_root_handler=False)
    logging.getLogger("scrapy").setLevel(logging.INFO)

    # Set Flask logging level to INFO
    logging.getLogger("werkzeug").setLevel(logging.INFO)

    # Set httpx logging level to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # TODO improve logging
    # logging.getLogger("markdown2").setLevel(logging.CRITICAL)
    # logging.getLogger("weasyprint").setLevel(logging.CRITICAL)
    # logging.getLogger("tzlocal").setLevel(logging.CRITICAL)
    # logging.getLogger("fontTools").setLevel(logging.CRITICAL)
