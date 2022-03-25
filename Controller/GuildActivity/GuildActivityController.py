from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Controller.AbstractController import AbstractController
from Controller.GuildActivity.EventRecurrence import EventRecurrence


class GuildActivityController(AbstractController):

    def __init__(self):
        super().__init__()
        self.engine = create_engine("sqlite:///test.db")
        declarative_base().metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)
        self.command_handlers = {
            "act": self._process_random_command,
        }

    async def _process_random_command(self, message):
        transaction = self.session()

        rec = EventRecurrence()
        rec.id = 0
        rec.title = "Daily"

        transaction.add(rec)

        transaction.commit()
        transaction.close()


