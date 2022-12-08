from os import getenv
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = getenv('SECRET_KEY', None)
assert SECRET_KEY

SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', None)
assert SQLALCHEMY_DATABASE_URI

API_NBA_KEY = getenv('API_NBA_KEY', None)
assert API_NBA_KEY
