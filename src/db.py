"""
Database logging module for storing case scrape history using SQLAlchemy.

Tables:
    logs: Stores logs of each successful case scrape. Uses a composite primary key of 'time_stamp', 'case_type', 'case_number'.
    (time_stamp will be different even if user requests same case)

"""
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
    """
    SQLAlchemy model for the 'logs' table.

    Attributes:
        time_stamp (str): UNIX timestamp at which the record was logged.
        case_type (str): The type of the case.
        case_number (str): The case number.
        case_year (int): The filing year of the case.
        data (str): JSON-encoded string containing raw response.
    """

    __tablename__ = 'logs'
    time_stamp = Column(String(25), nullable=False)
    case_type = Column(String(50), nullable=False)
    case_number = Column(String(50), nullable=False)
    case_year = Column(Integer, nullable=False)
    data = Column(Text)

    __table_args__ = (
        PrimaryKeyConstraint('time_stamp', 'case_type', 'case_number', name='pk_logs'),
    )

    def __init__(self, case_type: str, case_number: str, case_year: int, data: dict):
        """
        Initializes a new log entry.

        Args:
            case_type (str): Type of the case.
            case_number (str): Case number.
            case_year (int): Year the case was filed.
            data (dict): Raw response to be stored as JSON.
        """
        self.time_stamp = str(datetime.timestamp(datetime.now()))
        self.case_type = case_type
        self.case_number = case_number
        self.case_year = case_year
        self.data = json.dumps(data)

# Create table if it does not exist
Base.metadata.create_all(engine)

def insert_log(case_type: str, case_number: str, case_year: int, data: dict) -> bool:
    """
    Inserts a new log entry into the database.

    Args:
        case_type (str): The type of the case.
        case_number (str): The case number.
        case_year (int): The year of the case.
        data (dict): Raw data or metadata to log (will be stored as JSON).

    Returns:
        bool: True if insert was successful, False otherwise.
    """
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
