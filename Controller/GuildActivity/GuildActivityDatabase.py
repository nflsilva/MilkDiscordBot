from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid

base = declarative_base()
engine = create_engine("sqlite:///test_event.db")


class EventRecurrence(base):
    __tablename__ = "event_recurrence"
    id = Column("id", String, primary_key=True)
    title = Column("title", String)


class EventParticipant(base):
    __tablename__ = "event_participant"
    participant_id = Column("participant_id", String, primary_key=True)
    event_id = Column(String, ForeignKey("event.id"), primary_key=True)
    participant_name = Column("participant_name", String)


class Event(base):
    __tablename__ = "event"
    id = Column("id", String, primary_key=True)
    title = Column("title", String)
    description = Column("description", String)
    start_date = Column("start_date", DateTime)
    end_date = Column("end_date", DateTime)
    owner_id = Column("owner_id", String)
    notify_at = Column("notify_at", DateTime)
    active = Column("active", Boolean)
    recurrence_id = Column(Integer, ForeignKey("event_recurrence.id"))


class RunescapeBoss(base):
    __tablename__ = "runescape_boss"
    id = Column("id", String, primary_key=True)
    name = Column("name", String)


class DatabaseHelper:

    __instance = None

    @staticmethod
    def get_instance():
        if DatabaseHelper.__instance is None:
            DatabaseHelper()
        return DatabaseHelper.__instance

    def __init__(self):
        if DatabaseHelper.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DatabaseHelper.__instance = self
            self.session_maker = sessionmaker(bind=engine)
            self.populate_event_recurrence()
            self.populate_runescape_bosses()

    def create_transaction(self):
        return self.session_maker()

    def populate_event_recurrence(self):
        transaction = self.create_transaction()
        recurrences = transaction.query(EventRecurrence).all()
        if len(recurrences) == 0:
            weekly = EventRecurrence()
            weekly.id = 0
            weekly.title = "Weakly"

            monthly = EventRecurrence()
            monthly.id = 1
            monthly.title = "Monthly"

            transaction.add(weekly)
            transaction.add(monthly)
            transaction.commit()
        transaction.close()

    def populate_runescape_bosses(self):
        transaction = self.create_transaction()
        bosses = transaction.query(RunescapeBoss).all()
        if len(bosses) == 0:
            bosses_names = ["Giant Mole",
                            "Bandos Godwards",
                            "Sara Godwars",
                            "Zammy Godwars",
                            "Armadyl Godwars",
                            "Chaos Fanatic",
                            "Crazy Archaeologist",
                            "Scorpia",
                            "King Black Dragon",
                            "Chaos Elemental",
                            "Vet'ion",
                            "Venenatis",
                            "Callisto",
                            "Tempoross",
                            "Wintertodt",
                            "Zalcano",
                            "Chambers of Xeric",
                            "Theatre of Blood",
                            "Jad",
                            "Inferno",
                            "The Gauntlet",
                            "The Corrupted Gauntlet",
                            "Barrows",
                            "Deranged Archaeologist",
                            "Dagannoth kings",
                            "Sarachnis",
                            "Kalphite Queen",
                            "Zulrah",
                            "Vorkath",
                            "Corp",
                            "The Nightmare",
                            "Nex"]
            for name in bosses_names:
                boss = RunescapeBoss()
                boss.id = str(uuid.uuid4().int)
                boss.name = name
                transaction.add(boss)
            transaction.commit()

        transaction.close()

    def add_event(self, title, description, start_data, owner_id, recurrence_id):
        transaction = self.create_transaction()

        nid = str(uuid.uuid4().int)
        event = Event()
        event.id = nid
        event.title = title
        event.description = description
        event.start_date = start_data
        event.owner_id = owner_id
        event.active = True
        event.recurrence_id = recurrence_id
        transaction.add(event)

        transaction.commit()
        transaction.close()
        return nid

    def add_participant_to_event(self, participant_id, event_id, participant_name):
        transaction = self.create_transaction()

        relation = EventParticipant()
        relation.participant_id = participant_id
        relation.event_id = event_id
        relation.participant_name = participant_name
        transaction.add(relation)

        transaction.commit()
        transaction.close()

    def remove_participant_from_event(self, participant_id, event_id):
        transaction = self.create_transaction()

        relations = transaction\
            .query(EventParticipant)\
            .filter(EventParticipant.participant_id == participant_id,
                EventParticipant.event_id == event_id
        ).all()

        for r in relations:
            transaction.delete(r)

        transaction.commit()
        transaction.close()

    def get_entity(self, entity):
        transaction = self.create_transaction()
        query = transaction.query(entity).all()
        transaction.close()
        return query


base.metadata.create_all(engine)
