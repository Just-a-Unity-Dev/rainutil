from .wyci import Wyci

async def setup(bot):
    await bot.add_cog(Wyci(bot))
