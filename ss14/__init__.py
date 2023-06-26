from .ss14 import SS14

async def setup(bot):
    await bot.add_cog(SS14(bot))
