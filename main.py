# File imports
import utils
import messages
import youtube
import spotify
# Dep imports
import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content
    if content == '>playlist':
        await message.channel.send(await messages.playlist())
    elif content == '>playlists':
        await message.channel.send(await messages.playlist())
    elif content == '>help':
        await message.channel.send(messages.help())
    elif content == '>ping':
        await message.channel.send('pong!')
    elif content.startswith('>add'):
        check = utils.isURL(content)
        if check == None:
            return
        elif check[0] == "yt":
            await youtube.add_to_playlist(check[1])
            await message.add_reaction('👍')
        elif check[0] == "sp":
            run = await spotify.add_to_playlist(check[1])
            if run:
                await message.add_reaction('👍')
            else:
                await message.add_reaction('👎')

client.run(utils.readAuth("discord")["token"])