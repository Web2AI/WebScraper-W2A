# logger_config.py
import logging
import colorama
from colorama import Fore, Style

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
    logging.basicConfig(
        level=logging.ERROR,  # Set log level to DEBUG
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    # Apply the custom formatter to all handlers
    logger = logging.getLogger()  # Get the root logger
    for handler in logger.handlers:
        handler.setFormatter(CustomFormatter())

    return logger
