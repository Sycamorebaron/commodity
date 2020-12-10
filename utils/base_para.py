import os
from sqlalchemy import create_engine

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_PATH, 'data')

INPUT_DATA_PATH = os.path.join(DATA_PATH, 'input')
OUTPUT_DATA_PATH = os.path.join(DATA_PATH, 'output')

eg = create_engine('postgresql://postgres:thomas@localhost:5432/commodity')