from discord.ext import commands
import constants
import discord


class HelpCog(commands.Cog):
    def __init__(self, bot):
        pass
    
    @commands.command(name='cursebreaker', aliases=['CURSEBREAKER'])
    async def real_help(self, ctx):
        embed = discord.Embed(color=constants.EMBED_COLOR)
        embed.add_field(name="startpuzzle", value=f"Starts the puzzle!\n Usage: {constants.BOT_PREFIX}startpuzzle", inline=False)
        embed.add_field(name="answer", value=f"Answer any of the current riddles. \nUsage: {constants.BOT_PREFIX}answer <your_answer>", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='help')
    async def fake_help(self, ctx):
        embed = discord.Embed(color=constants.EMBED_COLOR)
        embed.add_field(name='Nice Try!', value="Soni's Bot only helps those who have earned it.")
        await ctx.send(embed=embed)

    @commands.command(name='adminhelp')
    @commands.has_role('bot-whisperer')
    async def adminhelp(self, ctx):
        embed = discord.Embed(color=constants.EMBED_COLOR)
        embed.add_field(name="startpuzzle", value=f"Start a puzzle.\nUsage: {constants.BOT_PREFIX}startpuzzle\nNeeds to be done in a channel that is given access with {constants.BOT_PREFIX}addchannel", inline=False)
        embed.add_field(name="answer", value=f"Answer a cipher.\nUsage: {constants.BOT_PREFIX}answer <your_answer>\nNeeds to be done in the same channel as a currently running puzzle.", inline=False)
        embed.add_field(name="nameteam", value=f"Name a team.\nUsage: {constants.BOT_PREFIX}nameteam <(1,2,3)> <new_name>\nNote: Team 3 is reserved for testers.", inline=False)
        embed.add_field(name="getname", value=f"Get the name of a team.\nUsage: {constants.BOT_PREFIX}getname <(1,2,3)>", inline=False)
        embed.add_field(name="addchannel", value=f"Bind a channel to a team.\nUsage: {constants.BOT_PREFIX}addchannel <channel_name> <(1,2,3)>", inline=False)
        embed.add_field(name="reload", value=f"Reload the google sheet to update riddle values.\nUsage: {constants.BOT_PREFIX}reload\nNote: this is performed hourly without the command.", inline=False)
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(HelpCog(bot))