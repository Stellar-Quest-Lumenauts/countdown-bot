import discord
import datetime
import asyncio
import requests
import os

# Todo: Make this use a Data Source or something instead of hardcoding?
dates = [
  datetime.datetime(2021,5,17,13,0,0,0), 
  datetime.datetime(2021,5,21,1,0,0,0), 
  datetime.datetime(2021,5,24,13,0,0,0), 
  datetime.datetime(2021,5,28,1,0,0,0)
]

images = [
  "https://api.stellar.quest/badge/GC6XLPVFEVZO5SJ4PADO4KQVSITOHADJLR7RZEC4A3SYLA3FORKXRRHI?v=3",
  "https://api.stellar.quest/badge/GAQRBLAAKJNMXVNZKBFCJ6E2XVXTXBUOXIAOQQNJBCUXBCZKR3HOLT2S?v=3",
  "https://api.stellar.quest/badge/GAATGXGABT7HB7ALO3TAGVBVDE5B24LMSUQ3EKNCJHO5QBY4D5G5DZX5?v=3",
  "https://api.stellar.quest/badge/GBZS5RP2YJDCF5RAJHXOHUXSBXD5KTDASIVSGETDYYI6OTPUS5ZFKIYA?v=3" 
]

GUILD_ID = 763798356484161566
BOT_TOKEN = os.environ.get('BOT_TOKEN')

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
                  await client.user.edit(avatar=r.raw.read())

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

client = MyClient()
client.run(BOT_TOKEN)
