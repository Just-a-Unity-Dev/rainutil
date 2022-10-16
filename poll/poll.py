from redbot.core import commands, Config, checks
from pathlib import Path
import string
import re

class Poll(commands.Cog):
    """Create basic polls in seconds!"""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.script_location = Path(__file__).absolute().parent

    @commands.command(name="poll")
    async def poll_command(self, ctx: commands.Context, question: str, ranswers: str):
        """
        poll command
        this one is fairly advanced so theres that
        syntax: poll "ques tion" "answer1,answer2,answer3,etc"
        the first argument is the question which you can include spaces by "wrapping quotes around them"
        second question are the answers, wrapped around in quotes, only up to 9 are allowed.
        seperate each answer with , so you get "answer1,answer2,answer3" and etc
        """
        numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        emojinumbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        output = []
        answers = ranswers.split(",")
        output.append(f"Question: **{question}** *by {ctx.author.mention}*")
        for i, answer in enumerate(answers):
            output.append(f":{numbers[i]}: - {answer}")
        message = await ctx.send('\n'.join(output))
        for i, answer in enumerate(answers):
            await message.add_reaction(emojinumbers[i])
