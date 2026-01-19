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

def register_reload_command(bot):
    @bot.command(name="recarregue")
    @commands.is_owner()
    async def reloadall(ctx):
        from reload_utils import reload_manual
        from setup import setup_bot

        sucesso, falha = await reload_manual(bot)

        # reaplica setup após reload
        setup_bot(bot)

        msg = "♻️ **Reload concluído**\n\n"

        if sucesso:
            msg += "✅ Sucesso:\n" + "\n".join(f"- `{x}`" for x in sucesso) + "\n\n"

        if falha:
            msg += "❌ Falha:\n" + "\n".join(f"- `{x}` → {e}" for x, e in falha)

        await ctx.send(msg)
