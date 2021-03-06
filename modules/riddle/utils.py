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


def create_level_prep_embed(level, team_name) -> discord.Embed:
    embed = create_embed()
    embed.add_field(name=f"Level {level} Complete!", value=f"Well done, {team_name}! Level {level+1} will begin in 30 seconds.")
    return embed

#TODO: Remove this. We'll send this as part of the static puzzle, and 
# won't need it in the bot itself.
def get_opening_statement(team) -> discord.Embed:
    """
    Assemble the opening message to send to the team before their puzzle begins
    
    :param team: (int) the team ID of the invoked command
    :return embed: (discord.Embed) the embed that includes the welcome message
    """
    embed = create_embed()
    embed.add_field(name="Welcome to my Puzzle!", value=f"Welcome, {constants.TEAM_TO_HOUSES[team]}! Congratulations on making it this far in the puzzle. " + \
    "For this part, you will be tasked with solving ciphers in rapid succession. You will have " + \
    f"{constants.TIME_LIMIT} seconds to solve each of {constants.NUM_LEVELS} levels. Each level will increase in difficulty; Level 1 will have " + \
    "1 riddle, Level 2 will have 2 riddles... you get the idea. You will need to utilize teamwork and quick wit in order to " + \
    "defeat me! Your time will start when you receive the first puzzle, which will happen in about 30 seconds " + \
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
    embed_list = []
    embed = create_embed()
    embed.add_field(name=f"Level {level}", value=f"Welcome to level {level}! You will have {constants.TIME_LIMIT} " + \
    f"seconds to solve {level} ciphers, beginning now.", inline=False)
    embed_list.append(embed)
    for i in range(level):
        riddle_proposal = riddles.sample()
        duplicate_counter = 0
        while riddle_proposal.index.item() in used_riddle_ids:
            riddle_proposal = riddles.sample()
            duplicate_counter += 1
            # Uh we don't want to get stuck here forever. If they've gotten this many duplicates, f it I'm down for a dup
            if duplicate_counter > 50:
                break
        embed_list.append(create_embed())
        embed_list[-1].add_field(name=f"Cipher #{i+1}", value=f"{riddle_proposal[constants.RIDDLE].item()}", inline=False)
        embed_list[-1].set_image(url=riddle_proposal[constants.RIDDLE].item())
        riddle_answers.append(riddle_proposal[constants.ANSWER].item().replace(' ', ''))
        used_riddle_ids.append(riddle_proposal.index.item())
    embed_list.append(create_embed())
    embed_list[-1].add_field(name="Answering", value=f"Use {constants.BOT_PREFIX}answer to make a guess on any of the ciphers.",
                    inline=False)
    return embed_list, used_riddle_ids, riddle_answers


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
    #embed = create_embed()
    if user_answer in current_answers:
            #embed.add_field(name=f"Correct for Riddle #{current_answers.index(user_answer)+1}", value=f"{user_answer} is the correct answer! Only {len(current_answers)-1} riddles left for this level!")
            current_answers.pop(current_answers.index(user_answer))
            result = constants.CORRECT
    else:
        #embed.add_field(name=f"Incorrect!", value=f"{user_answer} is NOT one of the correct answers!")
        result = constants.INCORRECT

    return result #embed, result


def create_solved_embed(team, team_name, answer) -> discord.Embed:
    """
    Create embed which has the answer to the puzzle.

    :param team: (int) the team ID
    :param answer: (str) the puzzle answer

    :return embed: (discord.Embed) the embed containing the puzzle answer
    """
    embed = create_embed()
    embed.add_field(name="Congratulations!", value=f"Congrats, {team_name} on a job well done! You successfully solved all {constants.NUM_LEVELS} levels. Here is the answer to the puzzle", inline=False)
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


