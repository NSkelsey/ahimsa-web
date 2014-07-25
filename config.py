"""Application config"""
import os

# Path related configuration
__home__ = os.path.expanduser('~')

CURDIR         = os.path.abspath(os.curdir)
AHIMSA_APP_DIR = os.path.join(__home__, '.ahimsa')

# DB Constants
DB_NAME = "pubrecord.db"
DB_PATH = os.path.join(AHIMSA_APP_DIR, DB_NAME)

# Development related
DEBUG   = True