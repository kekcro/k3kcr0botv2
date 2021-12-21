import os
import random
import time

import pandas as pd
import discord
import markovify

from dotenv import load_dotenv
from os.path import exists

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
guild = discord.Guild
text_models = {}
refreshing = False

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('with ma fukin silicon encrusted nuts'))

@client.event
async def on_message(message):
    global text_models
    global refreshing

    def prepare_markov(file_location):
        if exists(file_location):
            f = pd.read_csv(file_location)
            df = pd.DataFrame(f, columns=['author', 'content'])
            kdf = df.loc[df['author'] == 'kekcro']
            karr = kdf['content'].tolist()
            karrClean = [str(text) for text in karr]
            ktext = "\n".join(karrClean)
            return markovify.NewlineText(ktext)
        return None

    def prepare_model(file_location, guild_id):
        global text_models
        if exists(file_location):
            text_models[guild_id] = prepare_markov(file_location)
            return True
        return False

    def prepare_message(text_model):
        for i in range(50):
            answer = text_model.make_short_sentence(random.randint(300, 1000))
            if answer is not None:
                return answer
        return None

    def is_command(msg):
        if len(msg.content) == 0:
            return False
        elif 'hey kekcro, ' in msg.content:
            return True
        else:
            return False

    channel = message.channel
    if message.author == client.user:
        return

    elif message.content.startswith('hey kekcro, '):
        cmd = message.content.split('hey kekcro, ')[1].split()

        parameters = []
        if len(cmd) > 1:
            parameters = cmd[1:]

        if cmd[0] == 'help' and len(parameters) == 0:
            answer = discord.Embed(title="Command Info: `all`",
                                   description="""help - what you're asking for right now stupid!!
                                                    refresh <int> - gathers messages from the channel you're in to generate words and say funny things with. more info with `refresh help`""",
                                   colour=0x1a7794)
            await message.channel.send(embed=answer)

        if cmd[0] == 'refresh' and 0 <= len(parameters) <= 1:
            limit = 10000
            data = pd.DataFrame(columns=['content', 'time', 'author'])

            for parameter in parameters:
                if parameter == "help":
                    answer = discord.Embed(title="Command Info: `help`",
                                           description="""gathers messages from the channel you're in to generate words and say funny things with.
                                                            refresh <int> - where <number> is an optional integer of how many total messages to grab (default 10000, max 1000000)""",
                                           colour=0x1a7794)
                    await message.channel.send(embed=answer)
                    return
                elif parameter.isdigit():
                    limit = int(parameter)
                    if limit > 1000000:
                        limit = 1000000

            if not refreshing:
                answer = discord.Embed(title="security check",
                                       description="""sending u the epic code in console to make sure its u kekcro """,
                                       colour=0x1a7794)
                await message.channel.send(embed=answer)
                code = random.randint(111111, 999999)
                print(code)
                inputter = input("Input the 6 digit pin for security purposes")
                if str(code) != str(inputter):
                    answer = discord.Embed(title="security breach",
                                          description="u failed",
                                          colour=0x1a7794)
                    await message.channel.send(embed=answer)
                    return
                refreshing = True
                answer = discord.Embed(title="scraping da databaze",
                                       description="i am uploading it to the botnet",
                                       colour=0x1a7794)
                await message.channel.send(embed=answer)
                async for msg in channel.history(limit=limit):
                    if msg.author != client.user:
                        if not is_command(msg):
                            data = data.append({'content': msg.content,
                                                'time': msg.created_at,
                                                'author': msg.author.name}, ignore_index=True)
                        if len(data) == limit:
                            break

                if len(data) == 0:
                    answer = discord.Embed(title="fail",
                                           description="couldnt find any messages. try searching farther/supplying a int param. write `hey kekcro, help` for more advice.",
                                           colour=0x1a7794)
                    await message.channel.send(embed=answer)

                else:
                    file_location = f"{str(channel.guild.id) + '_' + str(channel.id)}.csv"
                    if exists(file_location):
                        data.to_csv(file_location, mode = 'a', header = False)
                    else:
                        data.to_csv(file_location)

                    answer = discord.Embed(title="done",
                                           description="thanks sucker",
                                           colour=0x1a7794)
                    await message.channel.send(embed=answer)
                refreshing = False

            else:
                answer = discord.Embed(title="im already scraping you asshat",
                                           description="learn 2 wait bitch",
                                           colour=0x1a7794)
                await message.channel.send(embed=answer)

    elif "kekcro" in message.content:
        if prepare_model(f"{str(channel.guild.id) + '_' + str(channel.id)}.csv", str(channel.guild.id)):
            answer = prepare_message(text_models[str(channel.guild.id)])
            if answer is not None:
                await message.channel.send(answer)
            else:
                # fail audibly
                answer = discord.Embed(title="could not generate a witty retort",
                                       description="double check the model / debug log mr. kekcro sir",
                                       colour=0x1a7794)
                await message.channel.send(embed=answer)
        else:
            # fail audibly
            answer = discord.Embed(title="could not generate a witty retort",
                                   description="double check the model / debug log mr. kekcro sir",
                                   colour=0x1a7794)
            await message.channel.send(embed=answer)

    else:
        if random.randint(0, 100) < 10:
            if prepare_model(f"{str(channel.guild.id) + '_' + str(channel.id)}.csv", str(channel.guild.id)):
                answer = prepare_message(text_models[str(channel.guild.id)])
                if answer is not None:
                    await message.channel.send(answer)
            else:
                # fail silently
                pass


client.run(TOKEN)
