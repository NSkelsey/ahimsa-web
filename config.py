'''Application config'''
import os

# Path related configuration
__home__ = os.path.expanduser('~')

CURDIR         = os.path.abspath(os.curdir)
#AHIMSA_APP_DIR = os.path.join(__home__, '.ahimsa')
#OMBUDS_APP_DIR = os.path.join(__home__, 'Library/Application Support/Ombudscore/node')

# DB Constants
#DB_NAME = 'pubrecord.db'
#DB_PATH = os.path.join(OMBUDS_APP_DIR, DB_NAME)
DB_PATH = os.path.join('./', 'pubrecord.db')

# Bitcoin Parameters
NETWORK = 'TestNet3'

# Development related
DEBUG   = True

BLK_DAY_STRF = '%Y-%m-%d' 

API_HOST = "localhost:1055"

API_URL = "http://" + API_HOST + "/api"
