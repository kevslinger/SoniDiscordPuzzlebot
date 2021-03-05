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

load_dotenv()


class RiddleCog(commands.Cog):
    def __init__(self, bot):
        # Bot and riddle initializations
        self.bot = bot
        self.current_level = [1, 1, 1]
        self.current_answers = [[], [], []]
        self.used_riddle_ids = [[], [], []]
        self.currently_puzzling = [False, False, False]
        self.answer = "Jurgen Schmidhuber" # TODO: Real answer here
        self.team1_id = int(os.getenv("TEAM1_CHANNEL_ID"))
        self.team2_id = int(os.getenv("TEAM2_CHANNEL_ID"))
        self.team3_id = 0

        # Google Sheets Authentication and Initialization
        self.client = utils.create_gspread_client()

        self.sheet_key = os.getenv('SHEET_KEY').replace('\'', '')
        self.sheet = self.client.open_by_key(self.sheet_key).sheet1
        self.riddles = pd.DataFrame(self.sheet.get_all_values(), columns=[constants.RIDDLE, constants.ANSWER])
        
        # Reload the google sheet every hour
        #bot.loop.create_task(self.reload(bot, self.sheet_key, self.client))
        bot.loop.create_task(self.reload())

    def get_team(self, channel_id):
        if channel_id == self.team1_id:
            team = 0
        elif channel_id == self.team2_id:
            team = 1
        elif channel_id == self.team3_id:
            team = 2
        else:
            print(f"invalid team. channel id is {channel_id} and team3_id is {self.team3_id}")
            team = -1
        return team
            
    @commands.command(name='startpuzzle')
    async def startpuzzle(self, ctx):
        """
        Start your puzzle! You will have 60 seconds per level to solve the riddles
        Usage: ~startpuzzle
        """
        team = self.get_team(ctx.channel.id)
        if team < 0:
            print("Startpuzzle called from an invalid channel!")
            await ctx.send("Cannot start a puzzle from this channel.")
            return
        # Housekeeping
        print(f"Received startpuzzle from team {constants.TEAM_TO_HOUSES[team]}")
        if self.currently_puzzling[team]:
            return
        else:
            self.reset_riddle(team)
            self.currently_puzzling[team] = True
        # TODO: DELETE THIS (welcome statement will be part of the static puzzle, not the bot)
        # Get opening introductory Statement
        #opening_statement_embed = utils.get_opening_statement(ctx, team)
        #await ctx.send(embed=opening_statement_embed)
        #time.sleep(10)

        # Creates the embed containing the riddles for that level as well as updates the IDs we're using and the acceptable answers for the level
        embeds, self.used_riddle_ids[team], self.current_answers[team] = utils.create_riddle_embed(ctx, 1, self.riddles, self.used_riddle_ids)
        for embed in embeds:
            await ctx.send(embed=embed)
        #await ctx.send(embeds=embeds)

        # Set a timer that will go off if the team hasn't completed all the riddles
        # for the level
        timer = Timer(constants.TIME_LIMIT, self.send_times_up_message, callback_args=(ctx, team, self.current_level[team]), callback_async=True)
        # TODO: do we even need any of this asyncio stuff
        # TODO: delete, seems like it goes on its own.
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(timer.wait())

    async def send_times_up_message(self, ctx, team, level):
        """
        After X seconds, the team's time is up and if they haven't solved all the riddles,
        They need to restart their 
        """
        # If there are no answers left, we assume the team solved the round
        if len(self.current_answers[team]) < 1 or self.current_level[team] != level:
            print(f"{constants.TEAM_TO_HOUSES[team]}'s time is up, but they have completed the level!")
            return
        
        print(f"{constants.TEAM_TO_HOUSES[team]}'s time is up, unlucky.")
        # Create an embed to send to the team. 
        embed = discord.Embed(color=constants.EMBED_COLOR)
        embed.add_field(name="Time's up!", value=f"Sorry, {constants.TEAM_TO_HOUSES[team]}! Your time is up. You still had {len(self.current_answers[team])} riddles left to solve for level {level}. If you'd like to re-attempt the puzzle, use the ~startpuzzle command!")
        await ctx.send(embed=embed)
        self.currently_puzzling[team] = False
        return

    
    @commands.command(name='addchannel')
    @commands.has_role("Co-Prefects")
    async def addchannel(self, ctx):
        """
        Argument to add a team's channel
        Usage: ~addchannel <channel_name> <{1, 2}>
        """
        # Remove command
        print(ctx.message.content)
        print("Received ~addchannel")
        user_args = ctx.message.content.replace(f'{constants.BOT_PREFIX}addchannel', '').strip()
        tokens = user_args.split()

        channel = discord.utils.get(ctx.guild.channels, name=tokens[0].strip())
        print(channel.id)
        embed = utils.create_embed()
        if int(tokens[1]) == 1:
            self.team1_id = channel.id
        elif int(tokens[1]) == 2:
            self.team2_id = channel.id
        elif int(tokens[1]) == 3:
            self.team3_id = channel.id
        else:
            embed.add_field(name='Incorrect Usage',
            value='Usage: ~addchannel <channel_name> <{1, 2}>')
            await ctx.send(embed=embed)
            return

        embed.add_field(name="Success",
            value=f"Successfully updated Team {int(tokens[1])}'s channel to {tokens[0]}")
        await ctx.send(embed=embed)


    # Command to check the user's answer. They will be replied to telling them whether or not their answer is correct
    @commands.command(name='answer', aliases=['a'])
    async def answer(self, ctx):
        """
        Check your  answer
        Usage: ~answer <your answer>
        """
        team = self.get_team(ctx.channel.id)
        if team < 0:
            print("answer called from an invalid channel!")
            await ctx.send("Cannot answer a riddle from this channel.")
            return
        # log command in console
        print(f"Received answer from {constants.TEAM_TO_HOUSES[team]}")
        print(f"All current answers: {self.current_answers}")
        # if the team isn't puzzling then we need to instruct them to use startpuzzle command first.
        if not self.currently_puzzling[team]:
            embed = utils.create_no_riddle_embed()
            await ctx.send(embed=embed)
            return 
        # Remove the command and any etraneous whitespace from the answer.
        user_answer = ctx.message.content.replace(f'{constants.BOT_PREFIX}answer', '').strip()
        print(f"Current answers are {self.current_answers[team]}")
        embed = utils.create_answer_embed(team, user_answer, self.current_answers[team])
        
        await ctx.send(embed=embed, reference=ctx.message, mention_author=True)
        
        if len(self.current_answers[team]) >= 1:
            return
        # If there are no answers left for the round, then either the team has completed the level, or the team has completed the entire puzzle.
        self.current_level[team] += 1
        if self.current_level[team] > 5:
            # Congratulate Team for solving the puzzle
            embed = utils.create_solved_embed(team, self.answer)
            self.currently_puzzling[team] = False
            print(f"{constants.TEAM_TO_HOUSES[team]} has solved the puzzle!")
            await ctx.send(embed=embed)
        else:
            # Create the next level embed
            embeds, self.used_riddle_ids[team], self.current_answers[team] = utils.create_riddle_embed(ctx, self.current_level[team], self.riddles, self.used_riddle_ids[team])
            for embed in embeds:
                await ctx.send(embed=embed)
            # Start the timer again
            timer = Timer(constants.TIME_LIMIT, self.send_times_up_message, callback_args=(ctx, team, self.current_level[team]), callback_async=True)
            #await ctx.send(embeds=embeds)
        

    @commands.command(name='reload')
    # TODO: Uncomment this so only co-prefects can reload riddle bot
    @commands.has_role('Co-Prefects')
    async def reload_sheet(self, ctx):
        """
        Reload the Google Sheet so we can update our riddles instantly.
        """
        self.riddles = pd.DataFrame(self.sheet.get_all_values(), columns=[constants.RIDDLE, constants.ANSWER])
        print(f"{constants.BOT_PREFIX}reload used. Reloaded riddle sheet")
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
            #sheet = client.open_by_key(sheet_key).sheet1
            self.riddles = pd.DataFrame(self.sheet.get_all_values(), columns=[constants.RIDDLE, constants.ANSWER])
            print("Reloaded riddle sheet")

    # Function to clean the bot's riddle so it can start a new one.
    def reset_riddle(self, team):
        self.current_level[team] = 1
        self.current_answers[team] = []
        self.used_riddle_ids[team] = []
        self.currently_puzzling[team] = False


def setup(bot):
    bot.add_cog(RiddleCog(bot))
