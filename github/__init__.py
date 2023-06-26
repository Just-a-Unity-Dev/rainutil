from .github import Github

def setup(bot):
    await bot.add_cog(Github(bot))
