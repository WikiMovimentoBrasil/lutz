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


class PeriodicityEnum(enum.Enum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'


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

    period_start = Column(DateTime)
    period_end = Column(DateTime)
    periodicity = Column(Enum(PeriodicityEnum))

    def to_dict(self):
        edit_count_total = (
            self.edits_male + self.edits_female + self.edits_neutral
        )
        out = {
            "wiki": self.wiki,
            "limit": self.limit,
            "timestamp": self.timestamp.isoformat(),
            "results": {
                '%_of_editors': {
                    "male": self.editors_male/self.limit,
                    "female": self.editors_female/self.limit,
                    "neutral": self.editors_neutral/self.limit,
                },
                "%_of_edits": {
                    "male": self.edits_male/edit_count_total,
                    "female": self.edits_female/edit_count_total,
                    "neutral": self.edits_neutral/edit_count_total,
                },
                "count": {
                    "male": self.editors_male,
                    "female": self.editors_female,
                    "neutral": self.editors_neutral,
                },
                "editcount": {
                    "male": self.edits_male,
                    "female": self.edits_female,
                    "neutral": self.edits_neutral,
                },
            }
        }
        if self.type == 'period':
            out['period_start'] = self.period_start
            out['period_end'] = self.period_end
            out['periodicity'] = self.periodicity
        return out
