import enum

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base


class SnapshotEnum(enum.Enum):
    recent = 'recent'
    historical = 'historical'


Base = declarative_base()


class Snapshot(Base):
    __tablename__ = "snapshot"

    id = Column(Integer, primary_key=True)
    wiki = Column(String(10))
    type = Column(Enum(SnapshotEnum))
    timestamp = Column(DateTime)
    editors_male = Column(Integer)
    editors_female = Column(Integer)
    editors_neutral = Column(Integer)
    edits_male = Column(Integer)
    edits_female = Column(Integer)
    edits_neutral = Column(Integer)
    limit = Column(Integer)
