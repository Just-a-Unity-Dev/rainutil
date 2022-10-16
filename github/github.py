from redbot.core import commands, Config, checks
from pathlib import Path
import discord
import string
import urllib
import json
import re

class Github(commands.Cog):
    """When You Code It!!! (x67)"""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.script_location = Path(__file__).absolute().parent
        self.config = Config.get_conf(self, 635473658356)

        self.iregex = r"\[(?:(\S+)#|#)?([0-9]+)\]"

        self.colors = [
            discord.Color(0x6CC644),
            discord.Color(0xFF4444),
            discord.Color(0x768390),
            discord.Color(0x6E5494)
        ]

        default_guild = {
            "servers": {},
            "github": {},
            "default_name": None,
        }
        self.config.register_guild(**default_guild)

    @commands.group()
    async def github(self, ctx):
        """
        Basic GitHub cogs

        Syntax: [prefix#id]
        """

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.config.guild(message.channel.guild).github() as github:
            for match in re.finditer(self.iregex, message.content):
                prefix = match.group(1)
                issue_id = int(match.group(2))
                keys = github.keys()
                for key in keys:
                    value = github[key]

                    if prefix == None:
                        default_name_c = self.config.guild(message.channel.guild).default_name
                        default_name = await default_name_c()
                        if default_name != None:
                            return await message.channel.send(
                                embed=self.get_github_embed(
                                    github[default_name]['url'],
                                    issue_id
                                )
                            )
                    
                    if str(value['prefix']) == str(prefix):
                        return await message.channel.send(embed=self.get_github_embed(value['url'], issue_id))
        
    def github_url(self, sub: str) -> str:
	    return f"https://api.github.com{sub}"
    
    def fix_body(self, body: str):
        new_body = []
        for line in body.splitlines():
            l = line.strip()
            header = False

            while l.startswith("#"):
                l = l[1:]
                header =  True
            if header:
                l = "**" + l + "**"

            if not l.startswith("<!--"):
                new_body.append(l)
        
        return '\n'.join(new_body)
	
    def get_github_embed(self, repo: str, issue_id: int):
            issue_url = self.github_url(f"/repos/{repo}/issues/{issue_id}")
            pr_url = self.github_url(f"/repos/{repo}/pulls/{issue_id}")

            issue_data = None
            pr_data = None
            
            issue_type = 2
            state = 0

            with urllib.request.urlopen(issue_url) as url:
                issue_data = json.load(url)
                # state
                # 0 - open
                # 1 - close
                # 2 - draft
                # 3 - merge
                
                if issue_data == None:
                    return
                elif issue_data['state'] == 'open':
                    state = 0
                elif issue_data['state'] == 'closed':
                    state = 1
            try:
                with urllib.request.urlopen(pr_url) as url:
                    pr_data = json.load(url)
                    # issue_type
                    # 0 - none
                    # 1 - issue
                    # 2 - PR

                    if pr_data['draft'] == True:
                        state = 2
                    elif pr_data['merged'] == True:
                        state = 3
            except urllib.error.HTTPError:
                issue_type = 1

            embed = discord.Embed()
            fixed_body = self.fix_body(issue_data['body'])
            body = (fixed_body[:500] + '...') if len(fixed_body) > 300 else fixed_body
            embed.title = issue_data['title']
            embed.url = f"https://github.com/{repo}/issues/{issue_id}"
            embed.description = body
            embed.color = self.colors[state]
            embed.set_author(name=issue_data['user']['login'], icon_url=issue_data['user']['avatar_url'])
            
            return embed

    @github.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def config(self,  ctx):
        """Configuration for GitHub"""
        pass

    @config.command(name="default")
    async def config_default(self, ctx: commands.Context, name):
        """Sets the default GitHub (if no prefix is defined)"""
        async with self.config.guild(ctx.guild).github() as github:
            if name not in github:
                return await ctx.send("That GitHub did not exist.")
                
        await self.config.guild(ctx.guild).default_name.set(name)
        return await ctx.send(f"Made `{name}` the default.")

    @config.command(name="add")
    async def config_add(self, ctx: commands.Context, name, url, prefix) -> None:
        """Adds a GitHub and prefix. [prefix#id]"""
        if name is None:
            return await ctx.reply("Lacking a `name`.")
        if prefix is None:
            return await ctx.reply("Lacking a `prefix`.")
        if url is None:
            return await ctx.reply("Lacking a `url`.")
        async with self.config.guild(ctx.guild).github() as github:
            github[name] = {
                "name": name,
                "prefix": prefix,
                "url": url,
            }
        return await ctx.reply(f"Created new github {name}.")
    
    @config.command("remove")
    async def config_remove(self, ctx: commands.Context, name):
        """Removes a GitHub via name."""
        if name is None:
            return await ctx.reply("Lacking a `name`.")
        
        async with self.config.guild(ctx.guild).github() as github:
            if name not in github:
                await ctx.send("That GitHub did not exist.")
                return
            del github[name]
        return await ctx.reply(f"Removed server {name}.")