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
#from threading import Timer
from aio_timers import Timer

load_dotenv()


# For this project, we have two teams
# Each team will have some roles (e.g. 'Ravenclaw' and 'Gryffindor' role will be one team)
# TODO: Can we restrict by channel not by role? (e.g. everyone in channel "Team A" will be able to use a command)
# So we can give each team a specific command to start the puzzle and answer the puzzle
# Only people with those roles can use those commands
# We need a few mutexes to prevent the ability for spam.
# We need a mutex over starting the puzzle. Once one person has started the puzzle, the process cannot be started
# again until that round has ended. 
# When someone starts a round, we will send them back level 1, which is 1 riddle and a 60 second timer
# If they answer the riddle 


# RIDDLE_ROLE_ID = int(os.getenv("RIDDLE_ROLE_ID")) #TODO: create riddle role?
class RiddleCog(commands.Cog):
    def __init__(self, bot):
        # Bot and riddle initializations
        self.bot = bot
        self.current_level = [1, 1]
        self.current_answers = [[], []]
        self.used_riddle_ids = [[], []]
        self.currently_puzzling = [False, False]
        self.answer = "Jurgen Schmidhuber"



        self.current_riddle = None
        self.current_riddle_possible_answers = None
        self.current_riddle_id = None
        self.current_riddle_hints = None
        self.current_given_hints = 0

        # Google Sheets Authentication and Initialization
        client = utils.create_gspread_client()

        sheet_key = os.getenv('SHEET_KEY').replace('\'', '')
        sheet = client.open_by_key(sheet_key).sheet1
        # TODO: Use Pandas Dataframe to store riddles?
        self.riddles = pd.DataFrame(sheet.get_all_values(), columns=[constants.RIDDLE, constants.ANSWER])
        
        #bot.loop.create_task(self.reload(bot, sheet_key, client))
            
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

        embed, self.used_riddle_ids[team], self.current_answers[team] = utils.create_riddle_embed(1, self.riddles, self.used_riddle_ids)
        await ctx.send(embed=embed)


        #t = Timer(constants.TIME_LIMIT, self.send_times_up_message, args=[ctx, team])
        timer = Timer(constants.TIME_LIMIT, self.send_times_up_message, callback_args=(ctx, team, self.current_level[team]), callback_async=True)
        # TODO: do we even need any of this asyncio stuff
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(timer.wait())

    async def send_times_up_message(self, ctx, team, level):
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


    # Command to check the user's answer. They will be replied to telling them whether or not their
    # answer is correct. If they are incorrect, they will be asked if they want a hint or to giveup
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
            self.riddles = sheet.get_all_values()[1:]
            print("Reloaded riddle sheet")

    # Function to clean the bot's riddle so it can start a new one.
    def reset_riddle(self, team):
        self.current_level[team] = 1
        self.current_answers[team] = []
        self.used_riddle_ids[team] = []
        self.currently_puzzling[team] = False


def setup(bot):
    bot.add_cog(RiddleCog(bot))
