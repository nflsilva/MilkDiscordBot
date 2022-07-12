from Controller.AbstractController import AbstractController
from Controller.GuildActivity.GuildActivityDatabase import DatabaseHelper, Event, EventRecurrence, EventParticipant, RunescapeBoss
import datetime


class GuildActivityController(AbstractController):

    def __init__(self):
        super().__init__()
        self.active = True
        self.databaseHelper = DatabaseHelper()
        self.command_handlers = {
            "event-start": self._process_start_command,
            "event-end": self._process_end_command,
            "event-members": self._process_members_command,
            "event-join": self._process_join_command,
            "event-leave": self._process_join_command,
        }

    async def _process_start_command(self, message):

        params = message.content.split(";")
        await message.delete()

        if len(params) != 3:
            await message.author.send(content=f"Usage: !event-start <Title>;<Description>;<Weekly|Monthly>")
            return

        if params[0][0] == " ":
            params[0][0] = params[0][1:]

        title_param = params[0]
        description_param = params[1]
        recurrence_param = params[2].lower()
        owner_id = message.author.id
        owner_name = message.author.name

        start_date = datetime.datetime.now()
        recurrence = 0
        if recurrence_param == "monthly":
            recurrence = 1

        event_id = self.databaseHelper.add_event(title_param, description_param, start_date, owner_id, recurrence)
        self.databaseHelper.add_participant_to_event(owner_id, event_id, owner_name)

        await message.channel.send(content=f"Created a {recurrence_param} event named {title_param}.", delete_after=5.0)

    async def _process_end_command(self, message):
        params = message.content.split(" ")
        await message.delete()

        if params[0] == "":
            params[0] = params[1:]

        if len(params) != 1:
            await message.author.send(content=f"Usage: !event-end <EventId>")
            return

        event_id = params[0]

        print("")

    async def _process_members_command(self, message):
        print("")

    async def _process_join_command(self, message):
        print("")

    async def _process_leave_command(self, message):
        print("")

    def test(self):
        eid = self.databaseHelper.add_event("Title", "Desc", datetime.datetime.now(), datetime.datetime.now(), 1)
        self.databaseHelper.add_participant_to_event(1, eid)
        self.databaseHelper.add_participant_to_event(2, eid)
        self.databaseHelper.remove_participant_from_event(1, eid)

        bosses = self.databaseHelper.get_entity(RunescapeBoss)
        print(bosses)

        events = self.databaseHelper.get_entity(Event)
        print(events)
