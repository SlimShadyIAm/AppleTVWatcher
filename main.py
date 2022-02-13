import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

async def on_message(self, message):
    print('Message from {0.author}: {0.content}'.format(message))

initial_extensions = [
    'cogs.watcher',
]

bot = commands.Bot(command_prefix="$",
                   description='Apple TV+ Watcher', case_insensitive=True)

if __name__ == '__main__':
    bot.remove_command("help")
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


@bot.event
async def on_ready():
    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(details='Apple TV+', state='Apple TV+', name='Apple TV+', type=discord.ActivityType.watching))
    print(f'Successfully logged in and booted...!')


bot.run(os.environ.get('APPLETV_TOKEN'), bot=True, reconnect=True)
