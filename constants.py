import os

from dotenv import load_dotenv

load_dotenv()

WINDOW_ILLEGAL_FILENAME_CHAR_LIST = ["\\", ":", "<", ">", "\"", "/", "|", "?", "*", " ", ".","[","]",]
LINUX_ILLEGAL_FILENAME_CHAR_LIST = ["/", "\0"]
MAC_ILLEGAL_FILENAME_CHAR_LIST = ["."]
GOLD_PAGE_SEARCH_LIMIT = 5000
NORMAL_PAGE_SEARCH_LIMIT = 1000
MAX_POST_PER_PAGE = 200

# Environment constants
# for the DB
DB_HOST = os.environ.get('DB_HOST')
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# for the Danbooru API
SITENAME = 'danbooru'
USERNAME = os.environ.get('USERNAME')
API_KEY = os.environ.get('API_KEY')

# for the downloading location
DEFAULT_DOWNLOAD_PARENT_LOCATION = os.environ.get("DEFAULT_FOLDER")