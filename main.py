import discord
import os
from dotenv import load_dotenv
import threading
import time
import asyncio


from Module.Twitch.TwitchController import TwitchController
from Module.PornHub.PornHubController import PornHubController
from Module.MusicPlayer.MusicPlayerController import MusicPlayerController

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_SERVER')
CHANNEL = os.getenv('DISCORD_CHANNEL')

client = discord.Client()
is_running = True


async def update_presence():
    game, url = await TwitchController.get_legacy_shack_activity()
    activity = discord.Streaming(name=game, url=url)
    await client.change_presence(activity=activity)


async def update_music_player():
    to_pop = []
    for guild_id in MusicPlayerController.voice_clients.keys():
        hidle_time = MusicPlayerController.voice_clients[guild_id]
        voice_clients = [x for x in client.voice_clients if x.guild.id == guild_id]

        if len(voice_clients) == 0:
            continue

        voice_client = voice_clients[0]
        if voice_client.is_playing():
            MusicPlayerController.voice_clients[guild_id] = 0
        else:
            hidle_time += 1
            MusicPlayerController.voice_clients[guild_id] = hidle_time

        if hidle_time >= 6:
            if voice_client.is_connected():
                asyncio.run_coroutine_threadsafe(voice_client.disconnect(), voice_client.loop)
            to_pop.append(guild_id)

    for g in to_pop:
        MusicPlayerController.voice_clients.pop(g)


def run():
    while is_running:
        if client.is_ready():
            #print("Starting background job cycle.")
            asyncio.run(update_presence())
            asyncio.run(update_music_player())
            #print("Ending background job cycle.")
            time.sleep(10)


t1 = threading.Thread(target=run)


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    t1.start()
    print("Ready!")


@client.event
async def on_message(message):

    #for guild in client.guilds:
        #if guild.name == GUILD:
        #    break
    ##await update_presence()

    if message.author == client.user:## or message.channel.name != CHANNEL:
        return

    trigger = "m!"

    message_text = message.content
    channel = message.channel
    author = message.author

    if message_text[:-len(message_text) + len(trigger)] == trigger:

        complete_command = message_text[len(trigger):]
        command_parts = complete_command.split(" ")
        opcode = command_parts[0]

        if opcode == "porn":
            async with message.channel.typing():
                await PornHubController.handle_command(complete_command, channel, author)

        elif opcode == "music":
            await MusicPlayerController.handle_command(complete_command, channel, author, message.guild.voice_client)

    #else:
        #await PornHubController.handle_surprise(channel, author, message_text.split(" "))

client.run(TOKEN)

print("Stopping background job...")
is_running = False
t1.join()
print("Done!")
