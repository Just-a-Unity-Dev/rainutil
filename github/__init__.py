from .github import Github

async def setup(bot):
    await bot.add_cog(Github(bot))
