import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'chatlocal.db'}")

motor_do_banco = create_engine(DATABASE_URL, echo=True)
sessaolocal = sessionmaker(bind=motor_do_banco, autoflush=False, autocommit=False)
