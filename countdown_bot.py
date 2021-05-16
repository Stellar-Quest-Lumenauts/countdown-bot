import discord
from discord.ext import commands
import datetime
import dateutil.parser
import asyncio
import requests
import json
import os
import sys

dates = []
images = []

GUILD_ID = 763798356484161566
BOT_TOKEN = os.environ.get('BOT_TOKEN')
SOURCE_URL = os.environ.get('SOURCE_URL')


def prepareData():
  """
  Fetch from the Stellar Quest API Endpoint to retrieve all the dates and images
  """
  response = requests.get(SOURCE_URL)
  if response.status_code != 200:
    print('There was an error fetching events...')
    sys.exit(1)

  data = json.loads(response.text)
  for elem in data['challenges']:
    print(f"Downloaded Event on: {elem['date']}")
    dates.append(dateutil.parser.parse(elem['date']).replace(tzinfo=None))
    images.append(f"https://api.stellar.quest/badge/{elem['badges']['main']}?v3")


def checkDate(currentDate):
    """
    Check if there's a new date to compare with to swap or not.
    """
    for ind, date in enumerate(dates):
        c = date - currentDate 
        if c.days < 0:
          dates.pop(ind)
          images.pop(ind)
        else:
          return (date, images[ind])

def getCountdown(c):
    """
    Parse into a Friendly Readable format for Humans
    """
    days = c.days
    c = c.total_seconds()
    hours = round(c//3600)
    minutes = round(c // 60 - hours * 60)
    seconds = round(c - hours * 3600 - minutes * 60)

    return days, hours, minutes, seconds

def createString(days, hours, minutes, seconds, fullText=False):
    """
    Create Different Readable Strings based on where that string should be used.
    """
    if days == 0:
        if fullText:
            string = f"{hours} Hours {minutes} Minutes {seconds} Seconds"
        else:
            string = f"{hours} H {minutes} M {seconds} S"
    else:
        hours = hours - (days * 24)
        if fullText:
            string = f"{days} Days {hours} Hours {minutes} Minutes {seconds} Seconds"
        else:
            string = f"{days} D {hours} H {minutes} M {seconds} S"

    return string

class MyClient(discord.Client):
    async def on_ready(self):
        """
        This is where the Magic happens 
        """
        print('Logged on as {0}!'.format(self.user))
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the clock while daydreaming of solving a new Quest")) # This is a Bad idea says StackOverFlow
        img = None

        while True:

            # Count the remaining time
            now = datetime.datetime.now()
            data = checkDate(now)
            b = data[0]
            image = data[1]
            c = b - now
          
            days, hours, minutes, seconds = getCountdown(c)

            # Update the Bot's nickname with the remaining time
            await client.get_guild(GUILD_ID).get_member(self.user.id).edit(nick=createString(days,hours,minutes,seconds))

            if img != image:
                # Update the image if it isn't the chosen one
                print(image)
                img = image
                filename = image.split("/")[-1]
                r = requests.get(image, stream = True)

                if r.status_code == 200:
                  r.raw.decode_content = True
                  #await client.user.edit(avatar=r.raw.read())

            await asyncio.sleep(1)

    async def on_message(self, message):
        """
        Check for messages and reply only if meant for the bot
        """
        if message.content.startswith('$$nextQuest'):
          print('Received Command...')

          now = datetime.datetime.now()
          data = checkDate(now)
          data = data[0]
          c = data - now
          days, hours, minutes, seconds = getCountdown(c)

          # Make a Fancy Embed to visually represent stuff
          title = f"The Next Stellar Quest is on { data.strftime('%d') } of {data.strftime('%B')} {data.year} at {data.strftime('%H')}:{data.strftime('%M')} UTC"
          embed=discord.Embed(title=title, url="https://quest.stellar.org", description="It'll have a lot of Stellar Magic but sadly nobody told me what the quest will be about :(", color=0x00fcff)
          embed.set_author(name="Stellar Quest - Countdown Bot")
          embed.add_field(name="Remaining Time", value=createString(days,hours,minutes,seconds, fullText=True), inline=False)
          embed.add_field(name="Convert to your timezone", value=f"https://time.is/{data.strftime('%H')}{data.strftime('%M')}_{ data.strftime('%d') }_{ data.strftime('%B') }_{data.year}_in_UTC?Stellar_Quest", inline=False)
          embed.set_footer(text="Created with Code, Love and Python")

          await message.reply(title, embed=embed)

if __name__ == '__main__':
  prepareData()
  client = MyClient()
  client.run(BOT_TOKEN)
