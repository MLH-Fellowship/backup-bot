import os
import csv
import json
import discord
import logging
import datetime
from discord.ext import commands
from . import logging as log
from dotenv import load_dotenv

def init():
    global logger
    global bot
    log.init()
    load_dotenv()
    logger = logging.getLogger('backup-bot')
    bot = discord.ext.commands.Bot(command_prefix='backup/')
    try:
        os.mkdir("data")
        logger.info("Created data directory!")
    except FileExistsError:
        logger.info("data directory already exists! Overwritting existing data")
    try:
        os.mkdir("data/stats")
    except FileExistsError:
        pass
    try:
        os.mkdir("data/backup")
    except FileExistsError:
        pass

def get_channels():
    logger.info("Starting bot for stats...")
    bot.loop.create_task(get_ch())
    bot.run(os.getenv('TOKEN'))

def start_backup():
    logger.info("Starting bot for backup...")
    bot.loop.create_task(get_messages())
    bot.run(os.getenv('TOKEN'))

async def get_ch():
    await bot.wait_until_ready()
    logger.info("Getting data...")

    channel_stats = {}
    user_stats = {}

    total_count = 0
    channel_count = 0
    for channel in bot.get_all_channels():
        if not isinstance(channel, discord.channel.TextChannel):
            continue

        print(f"'{channel.name}'")

        async for message in channel.history(limit=None):
            if message.author.bot:
                continue

            name = f"{message.author.name}#{message.author.discriminator}"
            try:
                nick = message.author.nick
            except:
                nick = "<unknown>"

            if name in user_stats:
                user_stats[name][0] += 1
            else:
                user_stats[name] = [1, nick]

            channel_count += 1
            print(f" - {channel_count}", end='\r')

        channel_stats[channel.name] = channel_count
        total_count += channel_count
        channel_count = 0

        print("")

    logger.info("Saving stats...")
    save_users(user_stats)
    save_channel(channel_stats)
    logger.info("Stopping bot...")
    bot.loop.stop()

def save_channel(stats):
    OUTPUT_PATH = "data/stats/channel_stats.csv"
    writer = csv.writer(open(OUTPUT_PATH, "w+"))
    writer.writerow(["Channel Name", "Message Count"])

    for [name, count] in stats.items():
        writer.writerow([name, count])

def save_users(stats):
    OUTPUT_PATH = "data/stats/user_stats.csv"
    writer = csv.writer(open(OUTPUT_PATH, "w+"))
    writer.writerow(["User Name", "Nick Name", "Message Count"])

    for [name, [count, nick]] in stats.items():
        writer.writerow([name, nick, count])

async def get_messages():
    await bot.wait_until_ready()
    logger.info("Getting data backup...")

    channel_data = {}
    for channel in bot.get_all_channels():
        if isinstance(channel, discord.channel.VoiceChannel):
            continue
        
        if isinstance(channel, discord.channel.TextChannel):
            if str(channel.category) not in channel_data:
                channel_data[str(channel.category)] = {}
                logger.info(f"Getting messages from category: {str(channel.category)}")

            channel_data[str(channel.category)][str(channel)] = []
            async for message in channel.history(limit=None):
                try:
                    if not message.author.nick == None:
                        name = message.author.nick
                    else:
                        name = message.author.name
                except:
                    name = message.author.name
                
                mesasage_data = f"{message.created_at} - {name}: {message.clean_content}"
                if len(message.attachments) > 0:
                    for attachment in message.attachments: 
                        mesasage_data += f',{attachment.url}'
                channel_data[str(channel.category)][str(channel)].append(mesasage_data)
            channel_data[str(channel.category)][str(channel)].reverse()

    logger.info("Saving stats...")
    save_channel_chats(channel_data)
    logger.info("Stopping bot...")
    bot.loop.stop()

def save_channel_chats(messages):
    now = datetime.datetime.now()
    OUTPUT_PATH = f"data/backup/{str(now)}.json"
    json_content = json.dumps(messages, indent=4)
    
    with open(OUTPUT_PATH, "w") as outfile: 
        outfile.write(json_content) 
    
