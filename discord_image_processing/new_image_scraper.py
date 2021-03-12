import discord
import pandas as pd
from discord.ext import commands
import word_to_image
from dotenv.main import load_dotenv
import os
load_dotenv()

# Discord bot script to scrape the URLs of all attachments (images) in a discord channel
# Requires ENV environments (or .env) with DISCORD_CHANNEL_ID and DISCORD_TOKEN set respectively
# Saves list of URLs to a CSV with (ID, URL, CIPHER, ANSWER) format.
# NOTE: ID, CIPHER, and ANSWER are both assumed to exist and may not work for your use case.
# We uploaded images with filenames such as 168_mo.png
# So 168 is our ID and mo represents MORSE (see cipher_map below)
# We also have a list of words saved in word_to_image, which allows us to find the answer for each ID
# TODO: word list outdated

cipher_map = {
    'pi': 'pigpen',
    'mo': 'morse',
    'se': 'semaphore',
    'br': 'braille'
}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    img_urls = []
    new_channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    print(new_channel)
    idx = 1
    async for msg in new_channel.history(limit=2000):
        for attachment in msg.attachments:
            url = attachment.url
            img_id = int(url.split('/')[-1].split('_')[0])
            cipher = cipher_map[url.split('/')[-1].split('_')[1]]
            answer = word_to_image.WORD_LIST[img_id]
            img_urls.append([img_id, attachment.url, cipher, answer])
        print(idx)
        idx += 1
    df = pd.DataFrame(img_urls)
    df.to_csv('cipher_sheet.csv', header=False, index=False)
    print("Wrote to csv")
    exit(0)
        

if __name__ == '__main__':
    client = discord.Client()
    client.run(os.getenv('DISCORD_TOKEN'))


