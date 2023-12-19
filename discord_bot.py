import os
import discord


class DiscordClient:
    client = discord.Client()

    discord_token = os.environ['DISCORD_TOKEN']

    @client.event
    async def on_ready():
        print('readuy')
    
    @client.event
    async def on_message(message=""):
        if message.content.startswith('$note') and message.channel.name == "mvp":
            await message.channel.send('new note added')


    client.run(discord_token)

    @client.event
    async def close(client):
        print(f"{client.user} disconnected")