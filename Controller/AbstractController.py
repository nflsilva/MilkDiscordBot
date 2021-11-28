

class AbstractController:

    def __init__(self):
        self.command_handlers = {}
        self.reaction_handlers = {}

    async def process_message(self, message):
        message_parts = message.content.split(" ")
        if len(message_parts) < 1:
            return

        command = message_parts[0]
        if command in self.command_handlers.keys():
            message.content = message.content[len(command):]
            handler = self.command_handlers[command]
            await handler(message)

    async def process_reaction(self, reaction, user):
        if reaction.emoji in self.reaction_handlers.keys():
            handler = self.reaction_handlers[reaction.emoji]
            await handler(reaction, user)



