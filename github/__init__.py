from .github import Github

def setup(bot):
    bot.add_cog(Github(bot))