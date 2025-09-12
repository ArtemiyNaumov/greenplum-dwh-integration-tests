import os

BASE_PATH = os.path.split(os.path.abspath(__file__))[0]
TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates')
CHECKS_PATH = os.path.join(BASE_PATH, 'checks')
SQL_PATH = os.path.join(BASE_PATH, 'sql')