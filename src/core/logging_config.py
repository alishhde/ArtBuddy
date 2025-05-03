import logging
import sys
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }


    def format(self, record):
        # Get the color for this log level
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # Format the message with color
        record.levelname = f"{color}{record.levelname}{reset}"
        record.name = f"{color}{record.name}{reset}"
        
        return super().format(record)


def setup_logging(verbose: bool = False, level: Optional[int] = None) -> None:
    """
    Set up logging configuration with colored output.
    
    Args:
        verbose: Whether to enable verbose logging
        level: Optional logging level to override the default
    """
    # Create a handler that outputs to stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Set the formatter
    formatter = ColoredFormatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Get the root logger
    logger = logging.getLogger()
    
    # Remove any existing handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    
    # Add our handler
    logger.addHandler(handler)
    
    # Set the logging level
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.DEBUG if verbose else logging.CRITICAL)
