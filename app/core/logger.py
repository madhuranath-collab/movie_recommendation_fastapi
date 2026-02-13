'''This module configures a centralized logging system for the FastAPI application.

It ensures that all application events — such as authentication attempts, user
actions, database operations, and system events — are captured in both the
console and rotating log files.'''

import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Create logs directory if missing
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(LOG_DIR, "auth.log")

# Define log format (structured)
LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(module)s | "
    "message=%(message)s"
)

# Configure logger
logger = logging.getLogger("auth")
logger.setLevel(logging.DEBUG)  

# File handler (rotating)
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
