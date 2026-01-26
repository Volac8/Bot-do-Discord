from discord.ext import commands

def register_reload_command(bot):
    @bot.command(name="recarregue", aliases=["reload", "reloadall", "recarregar"])
    @commands.is_owner()
    async def reloadall(ctx):
        """
        Comando de hot-reload: recarrega TUDO sem reiniciar o bot
        Uso: Jarvis, recarregue
        """
        from reload_utils import reload_manual
        import time

        inicio = time.time()
        await ctx.send("🔄 **Iniciando reload...**")

        try:
            sucesso, falha = await reload_manual(bot)
            tempo = time.time() - inicio

            # Reconstrói o embed com resultado
            msg = f"♻️ **Reload concluído em {tempo:.2f}s**\n\n"

            if sucesso:
                msg += "✅ **Recarregados:**\n"
                msg += "\n".join(f"  • `{x}`" for x in sucesso)
                msg += "\n\n"

            if falha:
                msg += "❌ **Falhas:**\n"
                for nome, erro in falha:
                    # Limita o tamanho do erro para não ficar muito grande
                    erro_curto = erro[:100] + "..." if len(erro) > 100 else erro
                    msg += f"  • `{nome}`: {erro_curto}\n"

            # Se houver muitas linhas, divide em múltiplas mensagens
            if len(msg) > 2000:
                partes = [msg[i:i+1900] for i in range(0, len(msg), 1900)]
                await ctx.send(partes[0])
                for parte in partes[1:]:
                    await ctx.send(parte)
            else:
                await ctx.send(msg)

        except Exception as e:
            await ctx.send(f"❌ **Erro crítico no reload:** {str(e)}")
            print(f"[ERRO CRÍTICO NO RELOAD] {e}")
            import traceback
            traceback.print_exc()
