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
        self.current_level = [1, 1]
        self.current_answers = [[], []]
        self.used_riddle_ids = [[], []]
        self.currently_puzzling = [False, False]
        self.answer = "Jurgen Schmidhuber" # TODO: Real answer here

        # Google Sheets Authentication and Initialization
        client = utils.create_gspread_client()

        sheet_key = os.getenv('SHEET_KEY').replace('\'', '')
        sheet = client.open_by_key(sheet_key).sheet1
        self.riddles = pd.DataFrame(sheet.get_all_values(), columns=[constants.RIDDLE, constants.ANSWER])
        
        # Reload the google sheet every hour
        bot.loop.create_task(self.reload(bot, sheet_key, client))
            
    @commands.command(name='startpuzzle')
    async def startpuzzle(self, ctx):
        """
        Start your puzzle! You will have 60 seconds per level to solve the riddles
        Usage: >startpuzzle
        """
        team = utils.get_team(ctx.channel.id)
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
        embed, self.used_riddle_ids[team], self.current_answers[team] = utils.create_riddle_embed(1, self.riddles, self.used_riddle_ids)
        await ctx.send(embed=embed)

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
        embed.add_field(name="Time's up!", value=f"Sorry, {constants.TEAM_TO_HOUSES[team]}! Your time is up. You still had {len(self.current_answers[team])} riddles left to solve for level {level}. If you'd like to re-attempt the puzzle, use the >startpuzzle command!")
        await ctx.send(embed=embed)
        self.currently_puzzling[team] = False
        return


    # Command to check the user's answer. They will be replied to telling them whether or not their answer is correct
    @commands.command(name='answer', aliases=['a'])
    async def answer(self, ctx):
        """
        Check your  answer
        Usage: >answer <your answer>
        """
        team = utils.get_team(ctx.channel.id)
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
        else:
            # Create the next level embed
            embed, self.used_riddle_ids[team], self.current_answers[team] = utils.create_riddle_embed(self.current_level[team], self.riddles, self.used_riddle_ids[team])
            # Start the timer again
            timer = Timer(constants.TIME_LIMIT, self.send_times_up_message, callback_args=(ctx, team, self.current_level[team]), callback_async=True)
        await ctx.send(embed=embed)

    # Reload the Google sheet every hour so we can dynamically add
    # Without needing to restart the bot
    async def reload(self, bot, sheet_key, client):
        await bot.wait_until_ready()
        while True:
            await asyncio.sleep(3600) # 1 hour
            sheet = client.open_by_key(sheet_key).sheet1
            self.riddles = pd.DataFrame(sheet.get_all_values(), columns=[constants.RIDDLE, constants.ANSWER])
            print("Reloaded riddle sheet")

    # Function to clean the bot's riddle so it can start a new one.
    def reset_riddle(self, team):
        self.current_level[team] = 1
        self.current_answers[team] = []
        self.used_riddle_ids[team] = []
        self.currently_puzzling[team] = False


def setup(bot):
    bot.add_cog(RiddleCog(bot))
