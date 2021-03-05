from discord.ext import commands
import constants
import discord


class HelpCog(commands.Cog):
    def __init__(self, bot):
        pass
    
    @commands.command(name='help')
    async def help(self, ctx):
        embed = discord.Embed(color=constants.EMBED_COLOR)
        embed.add_field(name="startpuzzle", value=f"Starts the puzzle!\n Usage: {constants.BOT_PREFIX}startpuzzle", inline=False)
        embed.add_field(name="answer", value=f"Answer any of the current riddles. \nUsage: {constants.BOT_PREFIX}answer <your_answer>", inline=False)
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(HelpCog(bot))