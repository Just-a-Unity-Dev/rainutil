from redbot.core import commands, Config, checks
from pathlib import Path
import string
import random
import re

class Based(commands.Cog):
    """Based on what?"""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.script_location = Path(__file__).absolute().parent
        self.config = Config.get_conf(self, 9235893212)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        for match in re.finditer(r"^\s*(based|gebaseerd|basé|basato|basado|basiert|ベース)[\s*?.!)]*$", message.content):
            
            if match is None:
                return
    
            based = "Based on what?"
            unbased = "Not Based."

            if match.group(1).lower() == "gebaseerd":
                based = "Gebaseerd op wat?"
                unbased = "Niet Gebaseerd."
       
            elif match.group(1).lower() == "basiert":
                based = "Worüber?"
                unbased = "Nich basiert."
        
            elif match.group(1).lower() == "basé":
                based = "Sur quoi?"
                unbased = "Pas basé."

            elif match.group(1).lower() == "basado":
                based = "¿Basado en qué?"
                unbased = "No basado."
        
            elif match.group(1).lower() == "basato":
                based = "Basato su cosa?"
                unbased = "Non basato."
        
            elif match.group(1) == u"ベース":
                based = u"何に基づいてですか"
                unbased = u"ベースではない"
    
            elif match.group(1).lower() == "bunaithe":
                based = "Cad é ina bunaithe?"
                unbased = "Ní bunaithe."
    
            if random.random() > 0.005:
                await message.channel.send(based)
            else:
                await message.channel.send(unbased)
