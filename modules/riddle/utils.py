import discord
import gspread
import json
import os
import constants
from oauth2client.service_account import ServiceAccountCredentials


def create_embed() -> discord.Embed:
    """
    Create an empty discord embed with color.
    :return: (discord.Embed)
    """
    return discord.Embed(color=constants.EMBED_COLOR)


def get_team(channel_id) -> int:
    """
    Get team ID from current channel ID
    Support 2 channels (one for each team), any other channel is invalid

    :param channel_id: (int) the channel ID the received message was from
    :return team: (int) the team ID
    """
    if channel_id == constants.TEAM1:
            team = 0
    elif channel_id == constants.TEAM2:
        team = 1
    else:
        team = -1
    return team

#TODO: Remove this. We'll send this as part of the static puzzle, and 
# won't need it in the bot itself.
def get_opening_statement(ctx, team) -> discord.Embed:
    """
    Assemble the opening message to send to the team before their puzzle begins
    
    :param ctx: (discord.ext.commands.Context) the context the command was invoked under
    :param team: (int) the team ID of the invoked command
    :return embed: (discord.Embed) the embed that includes the welcome message
    """
    embed = create_embed()
    embed.add_field(name="Welcome to my Puzzle!", value=f"Welcome, {constants.TEAM_TO_HOUSES[team]}! Congratulations on making it this far in the puzzle. " + \
    "For this part of the puzzle, you will be tasked with solving riddles in rapid succession. You will have " + \
    f"{constants.TIME_LIMIT} seconds to solve each of {constants.NUM_LEVELS} levels. Each level will get gradually harder; Level 1 will have " + \
    "1 ridde, Level 2 will have 2 riddles, and so on. You will need to utilize teamwork and quick wit in order to " + \
    "defeat me! Your time will start (approximately) when you receive the first puzzle, which will happen shortly " + \
    "after you get this message. Good luck!")
    return embed


def create_riddle_embed(level, riddles, used_riddle_ids):
    """
    Function to create the riddle embed
    :param level: (int) The level of the current puzzle solvers
    :param riddles: (pandas.DataFrame) the current set of riddles
    :param used_riddle_ids: (list of int) The list of riddle ids the team has already seen

    :return embed: (discord.Embed) The embed we create for the riddle
    :return used_riddle_ids: (list of int) an updated used_riddle_ids
    :return riddle_answer: (list of str) the answers to the given riddles
    """
    riddle_answers = []
    embed = create_embed()
    embed.add_field(name=f"Level {level}", value=f"Welcome to level {level}! You will have {constants.TIME_LIMIT} " + \
    f"seconds to solve {level} riddles, beginning now.", inline=False)
    for i in range(level):
        riddle_proposal = riddles.sample()
        duplicate_counter = 0
        while riddle_proposal.index.item() in used_riddle_ids:
            riddle_proposal = riddles.sample()
            duplicate_counter += 1
            # Uh we don't want to get stuck here forever. If they've gotten this many duplicates, f it I'm down for a dup
            if duplicate_counter > 50:
                break
        embed.add_field(name=f"Riddle #{i+1}", value=f"{riddle_proposal[constants.RIDDLE].item()}", inline=False)
        riddle_answers.append(riddle_proposal[constants.ANSWER].item())
        used_riddle_ids.append(riddle_proposal.index.item())
    embed.add_field(name="Answering", value=f"Use {constants.BOT_PREFIX}answer to make a guess on any of the riddles.",
                    inline=False)
    return embed, used_riddle_ids, riddle_answers


def create_no_riddle_embed() -> discord.Embed:
    """
    Function to create an embed to say there is no riddle

    :return embed: (discord.Embed) The embed we create
    """
    embed = create_embed()
    embed.add_field(name="No Current Riddle", 
                    value=f"You haven't started the puzzle. To start, use command {constants.BOT_PREFIX}startpuzzle.",
                    inline=False)
    return embed



def create_answer_embed(team, user_answer, current_answers) -> discord.Embed:
    """
    Create the Discord embed to show when the user makes a guess

    :param team: (int) the team ID 
    :param user_answer: (str) the answer given by the user
    :param current_answers: (list of str) the remaining answers for that team in the level

    :return embed: (discord.Embed) the embed telling the user whether they answered correctly or not.
    """
    embed = create_embed()
    if user_answer in current_answers:
            embed.add_field(name=f"Correct for Riddle #{current_answers.index(user_answer)+1}", value=f"{user_answer} is the correct answer!")
            current_answers.pop(current_answers.index(user_answer))
    else:
        embed.add_field(name=f"Incorrect!", value=f"{user_answer} is NOT the correct answer!")

    return embed


def create_solved_embed(team, answer) -> discord.Embed:
    """
    Create embed which has the answer to the puzzle.

    :param team: (int) the team ID
    :param answer: (str) the puzzle answer

    :return embed: (discord.Embed) the embed containing the puzzle answer
    """
    embed = create_embed()
    embed.add_field(name="Congratulations!", value=f"Congrats, {constants.TEAM_TO_HOUSES[team]} on a job well done! You successfully solved all {constants.NUM_LEVELS} levels. Here is the answer to the puzzle", inline=False)
    embed.add_field(name="Puzzle Answer", value=answer)
    return embed

def create_gspread_client():
    """
    Create the client to be able to access google drive (sheets)
    """
    # Scope of what we can do in google drive
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    # Write the credentials file if we don't have it
    if not os.path.exists('client_secret.json'):
        json_creds = dict()
        for param in constants.JSON_PARAMS:
            json_creds[param] = os.getenv(param).replace('\"', '').replace('\\n', '\n')
        with open('client_secret.json', 'w') as f:
            json.dump(json_creds, f)
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
    return gspread.authorize(creds)


