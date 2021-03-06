import SimpleRequests
import json
from datetime import datetime, timedelta
from time import mktime
from mimetypes import MimeTypes
import sys
sys.path.append('..')
import modules.riddle.utils as utils
from dotenv.main import load_dotenv
import os
import argparse

load_dotenv()

# Return a Discord snowflake from a timestamp.
snowflake = lambda timestamp_s: (timestamp_s * 1000 - 1420070400000) << 22
# Return a timestamp from a Discord snowflake.
timestamp = lambda snowflake_t: ((snowflake_t >> 22) + 1420070400000) / 1000.

mimetype = lambda name: MimeTypes().guess_type(name)[0] \
    if MimeTypes().guess_type(name)[0] is not None \
    else 'application/octet-stream'


def get_day(day, month, year, hour, minute, second):
    """Get the timestamps from 00:00 to 23:59 of the given day.
    :param day: The target day.
    :param month: The target month.
    :param year: The target year.
    """

    min_time = mktime((year, month, day, hour, minute, second-1, -1, -1, -1))
    max_time = mktime((year, month, day, hour, minute, second, -1, -1, -1))
    #max_time = mktime((year, month, day, 23, 59, 59, -1, -1, -1))

    return {
        '00:00': snowflake(int(min_time)),
        '23:59': snowflake(int(max_time))
    }


def safe_name(name):
    """Convert name to a *nix/Windows compliant name.
    :param name: The filename to convert.
    """

    output = ""
    for char in name:
        if char not in '\\/<>:"|?*':
            output += char

    return output

def create_query_body(**kwargs):
    """Generate a search query string for Discord."""

    query = ""

    for key, value in kwargs.items():
        if value is True and key != 'nsfw':
            query += '&has=%s' % key[:-1]

    return query


class DiscordConfig(object):
    """Just a class used to store configs as objects."""

class Discord:
    """Experimental Discord scraper class."""
    def __init__(self, config='config.json', apiver='v6'):
        """Discord constructor"""

        
        self.api = apiver
        self.buffer = 1048576
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36",
            'authorization': "mfa.lYOgQXud-TaiwPQP-MZArfxAltwJLFRJIiELwx3KDybzPp06dF7Wh1BBCoipu8IvEz8pFLSCN6BxxPbr102V"
        }

        self.types = {'images': True}
        self.query = create_query_body(
            images=True
            #TODO: more?
        )

        self.serverid = 470251021554286602
        self.channelid = 817486536114831370
        self.img_urls = []

    def get_server_name(self):
        request = SimpleRequests.SimpleRequests(self.headers)
        server = request.grab_page(f'https://discordapp.com/api/{self.api}/guilds/{self.serverid}')

        if server is not None and len(server) > 0:
            return f"{self.serverid}_{safe_name(server['name'])}"

    def get_channel_name(self):
        request = SimpleRequests.SimpleRequests(self.headers)
        channel = request.grab_page(f'https://discordapp.com/api/{self.api}/channels/{self.channelid}')

        if channel is not None and len(channel) > 0:
            return f"{self.channelid}_{safe_name(channel['name'])}"


    def grab_channel_images(self):
        """Gets all images posted in the current month"""
        date = datetime.today()
        month = date.month
        hour = 19
        minute = 12
        second = 59
        while date.year >= 2021 and date.month >= month:
            request = SimpleRequests.SimpleRequests(self.headers)

            today = get_day(date.day, date.month, date.year, hour, minute, second)
            print(f"{hour}:{minute}:{second}")
            request.set_header('referer', f'https://discordapp.com/channels/{self.serverid}/{self.channelid}')
            content = request.grab_page(f"https://discordapp.com/api/{self.api}/channels/{self.channelid}/messages/search?min_id={today['00:00']}&max_id={today['23:59']}&{self.query}")

            try:
                if content is not None:
                    if content['messages'] is not None:
                        #print(len(content['messages']))
                        for messages in content['messages']:
                            for message in messages:
                                self.check_config_mimetypes(message)
            except TypeError:
                raise TypeError
                print("Got TypeError")
                pass
            
            #date += timedelta(days=-1)
            second -= 1
            if second <= 0:
                minute -= 1
                second = 59
                if minute < 0:
                    hour -= 1
                    minute = 59
                    if hour < 0:
                        date += timedelta(days=-1)
                        hour = 23
            print(len(self.img_urls))
        #print(self.img_urls)

    def check_config_mimetypes(self, source):

        for attachment in source['attachments']:
            if self.types['images'] is True:
                if mimetype(attachment['proxy_url']).split('/')[0] == 'image':
                    self.img_urls.append(attachment['url'])
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--append', action='store_true')
    args = parser.parse_args()

    ds = Discord()
    print(ds.get_server_name())
    print(ds.get_channel_name())
    ds.grab_channel_images()

    client = utils.create_gspread_client()
    sheet_key = os.getenv("SHEET_KEY").replace("\'", "")
    sheet = client.open_by_key(sheet_key).sheet1

    # TODO: url.split(...) is not what we want. We need some mapping from the filename to the answer.
    if args.append:
        sheet.append_rows([[url, url.split('/')[-1].split('.')[0]] for url in ds.img_urls])
    else:
        print(len(ds.img_urls))
        sheet.clear()
        sheet.update([[url, url.split('/')[-1].split('.')[0]] for url in ds.img_urls])