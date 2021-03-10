# ARITHMANCY PUZZLEBOT

~~Soni's super secret discord both which nobody can know about.~~

Discord race puzzlebot! Used as part of a community arithmancy puzzle in March, 2021.

## Current Comamnds for users
- `~help` is an uninformative help command 
- `~codebreaker` is the real help command
- `~startpuzzle` starts the puzzle
- `~answer <your_answer>` submits a guess to the bot
- `~giveup` sends a message which encourages the team to keep tryin!

When the `~startpuzzle` command is sent, the team gets 1 riddle to solve. If they can get it within the time limit (+/- 60 seconds), they will have defeated level 1, and move on to level 2, where they will receive two riddles. This goes on for 5 levels. If the team defeats level 5, they will be given the answer to the puzzle.

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

We include `.sample-env` which are the environment variables used. Most of them are only used for creating the google sheets client, and a few others are used for discord.

# Issues

If you find any issues, bugs, or improvements, please feel free to open an issue and/or pull request! Thank you!

Feel free to find me on discord, `@kevslinger` with any questions you may have!