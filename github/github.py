from redbot.core import commands, Config, checks
from pathlib import Path
import discord
import string
import urllib
import json
import re

class Github(commands.Cog):
    """Github cog"""

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
            "emojis": [
                "green_circle",
                "red_circle",
                "grey_question",
                "purple_circle",
            ],
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
                                embed=await self.get_github_embed(
                                    github[default_name]['url'],
                                    issue_id,
                                    message.guild
                                )
                            )
                    
                    if str(value['prefix']) == str(prefix):
                        return await message.channel.send(embed=await self.get_github_embed(value['url'], issue_id, message.guild))
        
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
	
    async def get_github_embed(self, repo: str, issue_id: int, guild):
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
            
            async def fix_title(title: str):
                async with self.config.guild(guild).emojis() as emojis:
                    selected = emojis[state]
                    if type(selected) == str:
                        return f":{selected}: {title}"
                    return f"<:{self.bot.get_emoji(selected).name}:{selected}> {title}"

            embed.title = await fix_title(issue_data['title'])

            fixed_body = self.fix_body(issue_data['body'])
            body = (fixed_body[:500] + '...') if len(fixed_body) > 300 else fixed_body
            
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
    
    @config.command("emoji")
    async def config_emoji(self, ctx: commands.Context, name, emoji):
        """Configure the servers emojis. `name` takes 4 arguments (open,close,draft,merge). `emoji` is an EMOJI ID."""
        if name is None:
            return await ctx.reply("Lacking a `name`.")
        if emoji is None:
            return await ctx.reply("Lacking an `emoji`.")
        if int(emoji) is None:
            return await ctx.reply("Lacking an `emoji`.")

        async with self.config.guild(ctx.guild).emojis() as emojis:
            def string_to_equivalent(stri: str):
                if stri == "open":
                    return 0
                if stri == "close":
                    return 1
                if stri == "draft":
                    return 2
                if stri == "merge":
                    return 3

            emojis[string_to_equivalent(name)] = int(emoji)
            return await ctx.reply(f"Set `{name}` to `{emoji}`")

    
    @config.command("reset_emoji")
    async def config_reset_emoji(self, ctx: commands.Context):
        """Resets emoji"""
        async with self.config.guild(ctx.guild).emojis() as emoji:
            emoji = [
                "green_circle",
                "red_circle",
                "purple_circle",
                "grey_question"
            ]
        ctx.reply("Reset all custom emoji's")

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
