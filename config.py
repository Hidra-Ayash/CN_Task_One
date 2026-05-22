import os
import logging
from logging.handlers import TimedRotatingFileHandler

# Central configuration for credentials and global defaults
SSH_USER = "admin"
SSH_PASS = "cisco123"
SSH_SECRET = "cisco"

# Logging level (string -> logging.getLevelName)
LOG_LEVEL = "INFO"

# Logging directory and file (daily rotating logs)
BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_BACKUP_DAYS = 14


def _setup_logging():
	os.makedirs(LOG_DIR, exist_ok=True)
	level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
	root = logging.getLogger()
	root.setLevel(level)

	# Add TimedRotatingFileHandler if not already present for this file
	existing_file_handlers = [h for h in root.handlers if isinstance(h, TimedRotatingFileHandler) and getattr(h, 'baseFilename', '') == os.path.abspath(LOG_FILE)]
	if not existing_file_handlers:
		fh = TimedRotatingFileHandler(LOG_FILE, when='midnight', interval=1, backupCount=LOG_BACKUP_DAYS, encoding='utf-8')
		fh.suffix = "%Y-%m-%d"
		fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
		root.addHandler(fh)

	# Ensure a console/stream handler exists
	if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
		ch = logging.StreamHandler()
		ch.setLevel(level)
		ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
		root.addHandler(ch)

	logging.captureWarnings(True)


_setup_logging()
