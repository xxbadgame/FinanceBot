import discord
from discord.ext import commands, tasks

import os

intents = discord.Intents.all()  # Active les intents par défaut
bot = commands.Bot(command_prefix='!',description ='Voici mon bot de trading', intents=intents)


    
@bot.command()
async def bonjour(ctx):
    await ctx.send("Bienvenue chez Stratton Oakmont !")
    
@bot.command()
async def infoSociete(ctx):
    server = ctx.guild
    numberOfTextChannels = len(server.text_channels)
    numberOfVoiceChannels = len(server.voice_channels)
    serverDescription = server.description
    numberOfPerson = server.member_count
    serverName = server.name
    message = f"L'entreprise **{serverName}** regroupe {numberOfPerson} Strattonien sur-entrainé. \nDescritpion : Ouvrez votre Discord et travaillez. Je veux que vous régliez vos problèmes en devenant riches. \nNous possédons {numberOfTextChannels} salons textuels et {numberOfVoiceChannels} salons vocaux."
    await ctx.send(message)
    
    
channel_id =

@tasks.loop(seconds=1)
async def check_signal():
    with open("FinanceBot/Bot/signal.txt", "r") as file:
        signal = file.read().strip()
    channel = bot.get_channel(channel_id)
    if signal:
        await channel.send(f"{signal}")
    with open("FinanceBot/Bot/signal.txt", "w") as file:
        file.write("")

@bot.event
async def on_ready():
    print("Bot connecté")
    check_signal.start()


if __name__ == "__main__":
    bot.run('ODQyNDgyNTgyMTMwMjYyMDM2.GKCHpQ.34PCc7P7k8FViF71PQScp3wIspvwRnFuG3PXWA')
