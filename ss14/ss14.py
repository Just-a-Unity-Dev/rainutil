from redbot.core import commands, Config, checks
from pathlib import Path
import asyncio
import aiohttp
import base64

class SS14(commands.Cog):
    """Restart an SS14 server"""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.script_location = Path(__file__).absolute().parent
        self.config = Config.get_conf(self, 635473658356)
        self.issue = r"\[(?:(\S+)#|#)?([0-9]+)\]"
        default_guild = {
            "servers": {},
            "github": {}
        }
        self.config.register_guild(**default_guild)

    @commands.group()
    async def ss14(self, ctx: commands.Context) -> None:
        """SS14 commands."""
        pass

    @ss14.command(name="control")
    @checks.admin_or_permissions(manage_guild=True)
    async def control(self, ctx: commands.Context, name, type):
        if name is None:
            return await ctx.reply("Lacking a `name`.")
    
        await ctx.message.add_reaction("⏰")

        async with self.config.guild(ctx.guild).servers() as servers:
            if name not in servers:
                return await ctx.send("That server did not exist.")
            config = servers[name]
            try:
                base_url: str = config["url"]
                instance: str = config["key"]
                token: str = config["token"]

                if base_url.endswith("/"):
                    base_url = base_url[:1]

                url = base_url + f"/instances/{instance}/restart"

                if type == "update":
                    url = base_url + f"/instances/{instance}/update"
                elif type == "restart":
                    url = base_url + f"/instances/{instance}/restart"
                else:
                    return await ctx.reply("Invalid method. `update` or `restart` are the valid methods.")

                auth_header = "Basic " + base64.b64encode(f"{instance}:{token}".encode("ASCII")).decode("ASCII")

                async with aiohttp.ClientSession() as session:
                    async def load():
                        async with session.post(url, headers={"Authorization": auth_header}) as resp:
                            if resp.status != 200:
                                await ctx.reply(f"Wrong status code: {resp.status}")
                            else:
                                return await ctx.reply(f"Restarted `{name}`")
                    await asyncio.wait_for(load(), timeout=5)
            except asyncio.TimeoutError:
                return await ctx.reply("Server timed out.")
            except Exception as err:
                # wtf
                return await ctx.reply(f"Unexpected error occurred")

    @ss14.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def config(self, ctx: commands.Context) -> None:
        """
        Configuration for SS14
        """
        pass

    @config.command(name="addserver")
    async def config_addserver(self, ctx: commands.Context, name, server_url, instance, api_key) -> None:
        """USE THIS COMMAND IN A DM. THIS MAY RESULT IN LEAKING YOUR WATCHDOG API KEY."""
        if name is None:
            return await ctx.reply("Lacking a `name`.")
        if instance is None:
            return await ctx.reply("Lacking an `instance`.")
        if server_url is None:
            return await ctx.reply("Lacking a `server_url`.")
        if api_key is None:
            return await ctx.reply("Lacking a `api_key`.")
        async with self.config.guild(ctx.guild).servers() as servers:
            servers[name] = {
                "url": server_url,
                "key": instance,
                "token": api_key
            }
        return await ctx.reply(f"Created new server {name}.")

    @config.command("removeserver")
    async def config_removeserver(self, ctx: commands.Context, name):
        if name is None:
            return await ctx.reply("Lacking a `name`.")
    
        async with self.config.guild(ctx.guild).servers() as servers:
            if name not in servers:
                await ctx.send("That server did not exist.")
                return

            del servers[name]

        return await ctx.reply(f"Removed server {name}.")
