def register_events(bot):

    @bot.event
    async def on_ready():
        print(f"Bot online como {bot.user}")
