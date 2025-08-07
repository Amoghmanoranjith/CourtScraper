import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Text, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json
# Load environment variables
load_dotenv()
DB_URI = os.getenv("DB_URI")

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)

class Log(Base):
    __tablename__ = 'logs'

    time_stamp = Column(String(25), nullable=False)
    case_type = Column(String(50), nullable=False)
    case_number = Column(String(50), nullable=False)
    case_year = Column(Integer, nullable=False)
    data = Column(Text)

    __table_args__ = (
        PrimaryKeyConstraint('time_stamp', 'case_type', 'case_number', name='pk_logs'),
    )

    def __init__(self, case_type, case_number, case_year, data):
        self.time_stamp = str(datetime.timestamp(datetime.now()))
        self.case_type = case_type
        self.case_number = case_number
        self.case_year = case_year
        self.data = json.dumps(data)

# Create table if not exists
Base.metadata.create_all(engine)

def insert_log(case_type: str, case_number: str, case_year: int, data: str) -> bool:
    session = Session()
    try:
        log = Log(case_type, case_number, case_year, data)
        session.add(log)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("Duplicate entry. Composite key constraint violated.")
        return False
    except Exception as e:
        session.rollback()
        print(f"Error inserting log: {e}")
        return False
    finally:
        session.close()
