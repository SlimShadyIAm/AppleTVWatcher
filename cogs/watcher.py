import asyncio
import os
import sys
import traceback
from time import sleep

import discord
import feedparser
from discord.ext import commands, tasks


class AppleTVWatcher(commands.Cog):
    """Watch Apple TV+ feed for new posts."""

    def __init__(self, bot):
        self.bot = bot
        self.url = "https://apple.com/tv-pr/news-feed.xml"
        self.data_old = feedparser.parse(self.url)
        self.titles_old = [something["title"]
                           for something in self.data_old.entries]

        # create thread for loop which watches feed
        self.loop = self.watcher.start()

    # cancel loop when unloading cog
    def cog_unload(self):
        self.loop.cancel()

    # the watcher thread
    @tasks.loop(minutes=1.0)
    async def watcher(self):
        data = feedparser.parse(self.url)
        if len(data.entries) != 0:
            max_prev_date = max([something["updated_parsed"]
                                 for something in self.data_old.entries])
            new_posts = [post for post in data.entries if self.checks(
                post, max_prev_date)]
            # if there rae new posts
            if (len(new_posts) > 0):
                # check thier tags
                for post in new_posts:
                    print(f'NEW ENTRY: {post.title} {post.link}')
                    self.titles_old.append(post.title)
                    await self.push_update(post)

    def checks(self, post, max_prev_date):
        return post["updated_parsed"] > max_prev_date and post["title"] not in self.titles_old

    async def push_update(self, post):
        # which guild to post to depending on if we're prod or dev
        # post update to channel
        guild_ids = {
            457980242317934613: "software-updates",
            525250440212774912: "apple-tv",
            372449430495821825: "apple-tv"
        }

        for guild_id in guild_ids.keys():
            print(guild_id)
            guild = self.bot.get_guild(guild_id)
            print(guild)
            if guild is not None:
                guild_channels = self.bot.get_guild(guild_id).channels
                channel = discord.utils.get(
                    guild_channels, name=guild_ids[guild_id])
                if channel is not None:
                    await channel.send(f'New Apple TV+ blog post!\n{post.title}\n{post.link}')

    @ watcher.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

    @ watcher.error
    async def error(self, error):
        print("A watcher error occured")
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)
        await sleep(10)
        self.watcher.restart()


def setup(bot):
    bot.add_cog(AppleTVWatcher(bot))
