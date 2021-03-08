import random
from dotenv.main import load_dotenv
import discord
from discord.ext import commands
import asyncio
import os
import modules.riddle.utils as utils
import constants
import time
import pandas as pd
from aio_timers import Timer
from emoji import EMOJI_ALIAS_UNICODE_ENGLISH as EMOJIS

load_dotenv()


class RiddleCog(commands.Cog):
    def __init__(self, bot):
        # Bot and riddle initializations
        self.bot = bot
        self.current_level = [1, 1, 1]
        self.current_answers = [[], [], []]
        self.used_riddle_ids = [[], [], []]
        self.currently_puzzling = [False, False, False]
        self.answer = "SULPHUR VIVE"
        self.team_names = ["Team 1", "Team 2", "Testers"]
        # Set defaults to Arithmancy Team 1, Arithmancy Team 2, and Arithmancy prefect-team-1-bot
        self.team_channel_ids = [817232131373662268, 817232183982948362, 817817797043159100]

        # Google Sheets Authentication and Initialization
        self.client = utils.create_gspread_client()

        self.sheet_key = os.getenv('SHEET_KEY').replace('\'', '')
        self.sheet = self.client.open_by_key(self.sheet_key).sheet1
        self.riddles = pd.DataFrame(self.sheet.get_all_values(), columns=constants.COLUMNS)
        
        # Reload the google sheet every hour
        bot.loop.create_task(self.reload())

    def get_team(self, channel_id):
        # TODO: would 
        # if channel_id in self.team_channel_ids:
        #   return self.team_channel_ids.index(channel_id)
        # work?
        if channel_id == self.team_channel_ids[0]:
            team = 0
        elif channel_id == self.team_channel_ids[1]:
            team = 1
        elif channel_id == self.team_channel_ids[2]:
            team = 2
        else:
            print(f"invalid team")
            team = -1
        return team
            
    @commands.command(name='startrace')
    async def startpuzzle(self, ctx):
        """
        Start your race! You will have 60 seconds per level to solve the codes
        Usage: ~startrace
        """
        team = self.get_team(ctx.channel.id)
        if team < 0:
            print("startrace called from an invalid channel!")
            embed = utils.create_embed()
            embed.add_field(name="Can't do that!", value="Cannot solve that puzzle from this channel.")
            await ctx.send(embed=embed)
            return
        # Housekeeping
        print(f"Received startrace from team {self.team_names[team]}")
        if self.currently_puzzling[team]:
            return
        else:
            self.reset_riddle(team)
            self.currently_puzzling[team] = True

        # Creates the embeds containing the codes for that level as well as updates the IDs we're using and the acceptable answers for the level
        embeds, self.used_riddle_ids[team], self.current_answers[team] = utils.create_riddle_embed(1, self.riddles, self.used_riddle_ids)
        self.current_answers[team] = [answer.replace(' ', '') for answer in self.current_answers[team]]

        await ctx.send(embed=utils.get_opening_statement(self.team_names[team]))
        # In a short time, send the codes
        time = Timer(constants.BREAK_TIME, self.start_new_level, callback_args=(ctx, team, embeds), callback_async=True)

    async def send_times_up_message(self, ctx, team, level):
        """
        After X seconds, the team's time is up and if they haven't solved all the codess,
        They need to restart their race.
        """
        # If there are no answers left, we assume the team solved the round
        if len(self.current_answers[team]) < 1 or self.current_level[team] != level:
            print(f"{self.team_names[team]}'s time is up, and they have completed the level!")
            return
        
        print(f"{self.team_names[team]}'s time is up, unlucky.")
        # Create an embed to send to the team. 
        embed = discord.Embed(color=constants.EMBED_COLOR)
        embed.add_field(name="Time's up!", value=f"Sorry, {self.team_names[team]}! Your time is up. You still had {len(self.current_answers[team])} {constants.CODE} left to solve for level {level}. If you'd like to re-attempt the race, use the ~startrace command!", inline=False)
        embed.add_field(name="Answers", value=f"The answers to the remaining codes were:\n{chr(10).join(self.current_answers[team])}", inline=False)
        await ctx.send(embed=embed)
        self.currently_puzzling[team] = False
        return

    @commands.command(name='nameteam')
    @commands.has_role(constants.BOT_WHISPERER)
    async def nameteam(self, ctx):
        """
        Change the name of a team
        Usage: ~nameteam <{1, 2, 3}> <new_name>
        """
        print("Received ~namedteam")
        # Remove command from the input message.
        user_args = ctx.message.content.replace(f'{constants.BOT_PREFIX}nameteam', '').strip()
        tokens = user_args.split()

        embed = utils.create_embed()
        if 1 <= int(tokens[0]) <= 3:
            self.team_names[int(tokens[0])-1] = " ".join(tokens[1:])
            embed.add_field(name="Success",
            value=f"Successfully updated Team {int(tokens[0])}'s name to to {' '.join(tokens[1:])}")
        else:
            embed.add_field(name='Incorrect Usage',
            value='Usage: ~nameteam <{1, 2, 3}> <new_name>')
        await ctx.send(embed=embed)

    # TODO: Deprecated. Use getchannels instead
    @commands.command(name="getname")
    @commands.has_role(constants.BOT_WHISPERER)
    async def getname(self, ctx):
        """
        Get a team name
        Usage: ~getname <{1, 2, 3}>
        """
        print("Received ~getname")
        # Remove command from message input
        teamnum = ctx.message.content.replace(f'{constants.BOT_PREFIX}getname', '').strip()
        embed = utils.create_embed()
        if 1 <=int(teamnum) <= 3:
            embed.add_field(name="Sucess",
            value=f"Team {teamnum}'s name is {self.team_names[int(teamnum)-1]}")
        else:
            embed.add_field(name='Incorrect Usage',
            value='Usage: ~getname <{1, 2, 3}>')
        await ctx.send(embed=embed)


    @commands.command(name="getchannels")
    @commands.has_role(constants.BOT_WHISPERER)
    async def getchannels(self, ctx):
        """
        Get all channels and team names
        Usage: ~getchannels
        """
        print("Received ~getchannels")
        embed = utils.create_embed()
        for team in range(len(self.team_channel_ids)):
            embed.add_field(name=f"Team {team+1} Name", value=f"{self.team_names[team]}", inline=False)
            embed.add_field(name=f"Team {team+1} Channel", value=f"{self.bot.get_channel(self.team_channel_ids[team])}", inline=False)
        await ctx.send(embed=embed)
    


    @commands.command(name='addchannel')
    @commands.has_role(constants.BOT_WHISPERER)
    async def addchannel(self, ctx):
        """
        Argument to add a team's channel
        Usage: ~addchannel <channel_name> <{1, 2, 3}>
        Note: use ~addchannel 0 <{1, 2, 3}> to set team's channel to NONE
        """
        print("Received ~addchannel")
        # Remove command
        user_args = ctx.message.content.replace(f'{constants.BOT_PREFIX}addchannel', '').strip().replace('#', '') # TODO: remove replace('#', '')
        print(user_args)
        tokens = user_args.split()

        if tokens[0] == '0':
            self.team_channel_ids[int(tokens[1])-1] = None
            embed = utils.create_embed()
            embed.add_field(name="Success", value=f"Successfully removed channel from team {int(tokens[1])}")
            await ctx.send(embed=embed)
            return

        # TODO: better way to do this? Removing brackets seems hacky
        channel = self.bot.get_channel(int(tokens[0].replace('<', '').replace('>', '')))

        embed = utils.create_embed()
        if 1 <= int(tokens[1]) <= 3:
            self.team_channel_ids[int(tokens[1])-1] = channel.id
            embed.add_field(name="Success",
            value=f"Successfully updated Team {int(tokens[1])}'s channel to {channel}")
        else:
            embed.add_field(name='Incorrect Usage',
            value='Usage: ~addchannel <channel_name> <{1, 2, 3}>')

        await ctx.send(embed=embed)

    # Command to check the user's answer. They will be replied to telling them whether or not their answer is correct
    @commands.command(name='answer', aliases=['ANSWER'])
    async def answer(self, ctx):
        """
        Check your  answer
        Usage: ~answer <your answer>
        """
        team = self.get_team(ctx.channel.id)
        if team < 0:
            print("answer called from an invalid channel!")
            embed = utils.create_embed()
            embed.add_field(name="Can't do that!", value="Cannot solve that puzzle from this channel.")
            await ctx.send(embed=embed)
            return
        # log command in console
        print(f"Received answer from {self.team_names[team]}")
        print(f"All current answers: {self.current_answers}")
        # if the team isn't puzzling then we need to instruct them to use startpuzzle command first.
        if not self.currently_puzzling[team]:
            embed = utils.create_no_riddle_embed()
            await ctx.send(embed=embed)
            return 
        # Remove the command and whitespace from the answer.
        user_answer = ctx.message.content.replace(f'{constants.BOT_PREFIX}answer', '').strip().replace(' ', '') # TODO: strip is redundant since we're replacing all spaces?
        result = utils.get_answer_result(team, user_answer, self.current_answers[team])
        
        if result == constants.CORRECT:
            await ctx.message.add_reaction(EMOJIS[constants.CORRECT_EMOJI])
        else:
            await ctx.message.add_reaction(EMOJIS[constants.INCORRECT_EMOJI])

        # We pop off the correct answers as they are given, so at some point current_answers will be an empty list.
        # If there are more answers left, don't do any of that level complete nonsense.
        if len(self.current_answers[team]) >= 1:
            return
        # If there are no answers left for the round, then either the team has completed the level, or the team has completed the entire puzzle.
        if self.current_level[team] >= 5:
            # Congratulate Team for solving the puzzle
            embed = utils.create_solved_embed(self.team_names[team], self.answer)
            self.currently_puzzling[team] = False
            print(f"{self.team_names[team]} has solved the puzzle!")
            await ctx.send(embed=embed)
            return
        else:
            # Create the next level prep embed
            embed = utils.create_level_prep_embed(self.current_level[team], self.team_names[team])
            # Proceed to next level. Perform computation ahead of time.
            self.current_level[team] += 1
            # Creates all code embeds, updates used riddle IDS, and refreshes current answers for the next level.
            embeds, self.used_riddle_ids[team], self.current_answers[team] = utils.create_riddle_embed(self.current_level[team], self.riddles, self.used_riddle_ids[team])
            
            await ctx.send(embed=embed)
            time = Timer(constants.BREAK_TIME, self.start_new_level, callback_args=(ctx, team, embeds), callback_async=True)

    async def start_new_level(self, ctx, team, embeds):
        """
        Send the codes for the next level. Used on a timer
        So the next level is sent out after a predetermined
        Break time after the previous level was completed.
        Then, starts the timer for the level to end
        """
        for embed in embeds:
            await ctx.send(embed=embed)
        timer = Timer(constants.TIME_LIMIT, self.send_times_up_message, callback_args=(ctx, team, self.current_level[team]), callback_async=True)
        return

    @commands.command(name='reload', aliases=['RELOAD'])
    @commands.has_role(constants.BOT_WHISPERER)
    async def reload_sheet(self, ctx):
        """
        Reload the Google Sheet so we can update our codes instantly.
        Usage: ~reload
        """
        self.sheet = self.client.open_by_key(self.sheet_key).sheet1
        self.riddles = pd.DataFrame(self.sheet.get_all_values(), columns=constants.COLUMNS)
        print(f"{constants.BOT_PREFIX}reload used. Reloaded {constants.CODE} sheet")
        embed = utils.create_embed()
        embed.add_field(name="Sheet Reloaded",
        value="Google sheet successfully reloaded")
        await ctx.send(embed=embed)


    # Reload the Google sheet every hour so we can dynamically add
    # Without needing to restart the bot
    async def reload(self):
        await self.bot.wait_until_ready()
        while True:
            await asyncio.sleep(3600) # 1 hour
            self.sheet = self.client.open_by_key(self.sheet_key).sheet1
            self.riddles = pd.DataFrame(self.sheet.get_all_values(), columns=constants.COLUMNS)
            print(f"Reloaded {constants.CODE} sheet on schedule")

    # Function to clean the bot's riddle so it can start a new one.
    # UPDATE: Don't reset used riddle IDs. We have enough. Only do that on a forced ~reset
    def reset_riddle(self, team):
        self.current_level[team] = 1
        self.current_answers[team] = []
        self.currently_puzzling[team] = False

    @commands.command(name='reset')
    @commands.has_role(constants.BOT_WHISPERER)
    async def reset(self, ctx):
        """
        Reset the bot as if it has just loaded up
        Usage: ~reset
        Note: Does not reload google sheet. Use ~reload for that
        """
        for team in range(len(self.team_names)):
            self.current_level[team] = 1
            self.current_answers[team] = []
            self.used_riddle_ids[team] = []
            self.currently_puzzling[team] = False
        embed = utils.create_embed()
        embed.add_field(name="Success", value="Bot has been reset. I feel brand new!")
        await ctx.send(embed=embed)

    @commands.command(name='giveup')
    #@commands.has_role(constants.BOT_WHISPERER)
    async def giveup(self, ctx):
        """
        Give the answer to the team as if they had solved it.
        Usage: ~giveup
        """
        #embed = utils.create_solved_embed("Team,", self.answer)
        #await ctx.send(embed=embed)
        embed = utils.create_embed()
        embed.add_field(name="Giving up?", value="No! Never give up, never surrender!\n\nIf you need help using the bot, tag @help.\nIf you're unable to complete the race, consider using a hint.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RiddleCog(bot))
