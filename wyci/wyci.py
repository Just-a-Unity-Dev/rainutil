from redbot.core import commands, Config, checks
from pathlib import Path
import string
import re

class RainUtil(commands.Cog):
    """When You Code It!!! (x67)"""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.script_location = Path(__file__).absolute().parent
        self.config = Config.get_conf(self, 9235893212)
        default_guild = {
            "counter": 0
        }
        self.config.register_guild(**default_guild)

    async def remove_punctuation(self, x: str):
        return x.translate(str.maketrans('', '', string.punctuation))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        content: str = message.content
        count = 0
        for match in re.finditer(r"when$", self.remove_punctuation(content.lower())):
            async with self.config.guild(message.channel.guild).counter() as count:
                count += 1
                if count == 1:
                    return await message.channel.send("When You Code It!!!")
                else:
                    return await message.channel.send(f"When You Code It!!! (x{count})")
        
    @commands.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def config(self):
        """Configuration for WYCI"""
        pass

    @config.command(aliases=["resetcounter"])
    async def config_reset_counter(self, ctx: discord.Context):
        """Resets the WYCI counter"""
        async with self.config.guild(message.channel.guild).counter() as count:
            count = 0
        return await ctx.reply("Reset the WYCI counter.")
