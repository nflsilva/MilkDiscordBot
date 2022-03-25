from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class EventRecurrence(declarative_base()):

    __tablename__ = "event_recurrence"

    id = Column("id", Integer, primary_key=True)
    title = Column("title", String)
