from discord.ext import commands

def setup_bot(bot: commands.Bot):
    from core import register_events
    from reload_utils import register_reload_command

    register_events(bot)
    register_reload_command(bot)

    extensoes = [
        "comandos_personalizados",
        "evolucao"
    ]

    for ext in extensoes:
        if ext not in bot.extensions:
            bot.load_extension(ext)
