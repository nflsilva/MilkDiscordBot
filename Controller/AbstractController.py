

class AbstractController:

    def __init__(self):
        self.command_handlers = {}

    async def process_message(self, message):
        message_parts = message.content.split(" ")
        if len(message_parts) < 1:
            return
        try:
            command = message_parts[0]
            if command in self.command_handlers.keys():
                message.content = message.content[len(command):]
                handler = self.command_handlers[command]
                await handler(message)
        except:
            pass