from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


class Event(declarative_base()):

    __tablename__ = "event"

    id = Column("id", Integer, primary_key=True)
    title = Column("title", String)
    start_date = Column("start_date", DateTime)
    end_date = Column("end_date", DateTime)
    recurrence_id = Column(Integer, ForeignKey("event_recurrence.id"))
