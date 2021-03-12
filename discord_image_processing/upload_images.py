import discord
import pandas as pd
from discord.ext import commands
import word_to_image
import glob
import os
from dotenv.main import load_dotenv
load_dotenv()

# Script to take a directory of PNG files and upload them to a discord channel
# NOTE: this process may take a long time, depending on the number of files you wish to upload
# Discord limits each user to send something like 5 messages at a time, and has a sort of anti-spam mechanic
# All messages will be delivered, though


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    new_channel = client.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
    print(new_channel)
    idx = 1
    for img_path in glob.glob('../encoded_imgs/*.PNG'):
        await new_channel.send(file=discord.File(img_path))
        print(idx)
        idx += 1
    print("uploaded all images")
  

if __name__ == '__main__':
    client = discord.Client()
    client.run(os.getenv("DISCORD_TOKEN"))