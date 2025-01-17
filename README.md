# ARITHMANCY PUZZLEBOT

~~Soni's super secret discord both which nobody can know about.~~

Discord race puzzlebot! Used as part of a community arithmancy puzzle in March, 2021.

NOTICE: This repo is no longer supported. Please see [this repo](https://github.com/kevslinger/DiscordCipherRace) for continued development.

## Current Comamnds for users
- `~help` is an uninformative help command 
- `~codebreaker` is the real help command
- `~startrace` starts the puzzle
- `~answer <your_answer>` submits a guess to the bot
- `~giveup` sends a message which encourages the team to keep tryin!

When the `~startrace` command is sent, the team gets 1 riddle to solve. If they can get it within the time limit (+/- 60 seconds), they will have defeated level 1, and move on to level 2, where they will receive two riddles. This goes on for 5 levels. If the team defeats level 5, they will be given the answer to the puzzle.

This bot assumes we have 2 teams competing, and the bot will only take commands from ~~2~~ 3 specific channels -- 1 channel per team (and one team for testers). Any command outside said channels will receive an error message. 

## Additional Commands for Admins (with perms role)
- `~nameteam` lets you set the team name
- `~getname` lets you check the name for each team (deprecated: use `~getchannels`)
- `~getchannels` gets the team names and their respective channels for all teams
- `~addchannel` sets the channel for a specific team
- `~reload` reloads the set of codes from the google sheet
- `~reset` resets the previously seen code IDs (used for de-duping)

# Setup 
We recommend you create a virtual environment with python 3.7. Then, install dependencies. 

`pip install -r requirements.txt`

## Preprocessing

Before starting the bot, we first generated images with words encoded via 4 ciphers (Braille, Morse, Semaphore, and Pigpen). We gathered a set of words from the HP Wiki (scraper code found in `hpwikia`). After finalizing which words we would use, we encoded each word in the 4 ciphers, uploaded them to discord (this can probably be replaced by any other site to store images), and then stored the list of img URLs in a google sheet, along with a unique word ID number and the word that was encoded. The bot takes that sheet in order to supply the users with images as part of the race. The code for these image processing steps can be found in `discord_image_processing`.


## The Race Bot

[This page](https://github.com/googleapis/google-api-python-client/blob/master/docs/start.md) seems to have good information on how to get `Setup` and `Authentication and authorization`, which should help you get a `client_secret.json`, and then you can copy/paste those values inside the quotes for each value in `.env`.

[This tutorial](https://www.writebots.com/discord-bot-token/) should be a good way to create a bot, get the discord token, and add it to a server to be able to run the bot. After you've done all that, you can run the bot with `python bot.py` and it'll go online in the server.


# Issues

If you find any issues, bugs, or improvements, please feel free to open an issue and/or pull request! Thank you!

Feel free to find me on discord, `@kevslinger` with any questions you may have!
