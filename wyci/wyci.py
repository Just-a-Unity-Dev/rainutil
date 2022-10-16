from redbot.core import commands, Config, checks
from pathlib import Path
import string
import re

class Wyci(commands.Cog):
    """When You Code It!!! (x67)"""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.script_location = Path(__file__).absolute().parent
        self.config = Config.get_conf(self, 9235893212)
        default_guild = {
            "counter": 0
        }
        self.config.register_guild(**default_guild)

    @commands.group()
    async def wyci(self, ctx):
        """When You Code It!!! (x67)"""

    @commands.Cog.listener()
    async def on_message(self, message):
        for match in re.finditer(r"\S\s+(?:when|whence)[\s*?.!)]*$", message.content):
            counter = self.config.guild(message.channel.guild).counter
            count = await counter()
            await counter.set(count + 1)
            if (count + 1) <= 1:
                return await message.channel.send("When You Code It!!!")
            else:
                return await message.channel.send(f"When You Code It!!! (x{count + 1 })")
        
    @wyci.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def config(self,  ctx):
        """Configuration for WYCI"""
        pass

    @config.command(name="resetcounter")
    async def config_reset_counter(self, ctx):
        """Resets the WYCI counter"""
        count = self.config.guild(ctx.guild).counter
        await count.set(0)
        return await ctx.reply("Reset the WYCI counter.")
