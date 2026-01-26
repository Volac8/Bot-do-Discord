from datetime import datetime, timedelta
from discord.ext import commands
from utils.utils import agendar_notificacoes, carregar_agenda, get_scheduler, salvar_agenda
import asyncio

class Agenda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.agenda_rpg = carregar_agenda()

    @commands.command(name="agendar")
    async def agendar(self, ctx):
        """Agenda um RPG"""
        await ctx.send("📅 Envie a data e hora do RPG no formato `DD/MM/AAAA HH:MM`:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg_data = await self.bot.wait_for("message", timeout=60, check=check)
            data_str = msg_data.content.strip()
            new_start = datetime.strptime(data_str, "%d/%m/%Y %H:%M")

            for key, item in self.agenda_rpg.items():
                old_start = datetime.strptime(key, "%d/%m/%Y %H:%M")
                old_end = old_start + timedelta(minutes=item["duracao_min"])
                if new_start < old_end and new_start > old_start:
                    await ctx.send(
                        f"⚠️ Conflito de horário! Este RPG se sobrepõe ao agendado em `{key}`: **{item['descricao']}**"
                    )
                    return

            await ctx.send("⏱️ Qual a duração da sessão? Formato `HH:MM`")
            msg_dur = await self.bot.wait_for("message", timeout=30, check=check)
            h, m = map(int, msg_dur.content.strip().split(":"))
            new_dur_min = h * 60 + m

            chave = new_start.strftime("%d/%m/%Y %H:%M")
            await ctx.send("📝 Qual é a descrição da sessão?")
            msg_desc = await self.bot.wait_for("message", timeout=30, check=check)
            descricao = msg_desc.content.strip()

            await ctx.send("📛 Marque o cargo do RPG (ex: @Aventureiros).")
            msg_cargo = await self.bot.wait_for("message", timeout=30, check=check)

            if not msg_cargo.role_mentions:
                return await ctx.send("❌ Você precisa mencionar um cargo válido com `@nome_do_cargo`.")

            cargo = msg_cargo.role_mentions[0]

            self.agenda_rpg[chave] = {
                "autor": ctx.author.name,
                "descricao": descricao,
                "cargo_id": cargo.id,
                "canal_id": ctx.channel.id,
                "duracao_min": new_dur_min
            }
            salvar_agenda()
            agendar_notificacoes(self.bot, new_start, ctx.channel.id, cargo.id, descricao, new_dur_min)

            await ctx.send(
                f"✅ RPG agendado para {chave}, duração {h:02d}:{m:02d}, com cargo {cargo.mention}!"
            )

        except Exception as e:
            await ctx.send("⏰ Tempo esgotado ou erro de formato. Tente novamente.")
            print(f"[ERRO] agendar: {e}")

    @commands.command(name="listar")
    async def listar(self, ctx):
        """Lista os RPGs agendados"""
        self.agenda_rpg = carregar_agenda()
        if not self.agenda_rpg:
            return await ctx.send("📭 Nenhum RPG agendado.")

        linhas = []
        for i, data_str in enumerate(sorted(self.agenda_rpg), start=1):
            item = self.agenda_rpg[data_str]
            linhas.append(f"{i}. `{data_str}` – {item['descricao']}")

        texto = "📋 **Agenda de RPGs (use o número para excluir):**\n" + "\n".join(linhas)
        await ctx.send(texto)

    @commands.command(name="excluir")
    async def excluir(self, ctx, arg: str = ""):
        """Exclui um RPG da agenda"""
        self.agenda_rpg = carregar_agenda()
        if not self.agenda_rpg:
            return await ctx.send("📭 Nenhum RPG para excluir.")

        keys = sorted(self.agenda_rpg)

        if arg and arg.isdigit():
            idx = int(arg) - 1
            if 0 <= idx < len(keys):
                chave = keys[idx]
            else:
                return await ctx.send("❌ Índice inválido.")
        elif arg:
            chave = arg.strip()
            if chave not in self.agenda_rpg:
                return await ctx.send("❌ Não encontrei nenhum RPG nessa data/hora.")
        else:
            await ctx.send("🗑️ Digite o número ou a data/hora (DD/MM/AAAA HH:MM) do RPG a excluir:")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for("message", timeout=30, check=check)
                content = msg.content.strip()
                if content.isdigit():
                    idx = int(content) - 1
                    if 0 <= idx < len(keys):
                        chave = keys[idx]
                    else:
                        return await ctx.send("❌ Índice inválido.")
                else:
                    chave = content
                    if chave not in self.agenda_rpg:
                        return await ctx.send("❌ Não encontrei nenhum RPG nessa data/hora.")
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Tempo esgotado. Tente de novo.")

        info = self.agenda_rpg.pop(chave)
        salvar_agenda()
        await ctx.send(f"✅ RPG de `{chave}` ({info['descricao']}) excluído.")

    @commands.command(name="agendados")
    async def agendados(self, ctx):
        """Mostra todos os RPGs agendados"""
        self.agenda_rpg = carregar_agenda()
        if not self.agenda_rpg:
            await ctx.send("Tragicamente não há nenhum rpg agendado")
            return

        resposta = "📅 **Agenda de RPGs:**\n"
        for data_str in sorted(self.agenda_rpg):
            item = self.agenda_rpg[data_str]
            resposta += f"🕒 `{data_str}` - {item['descricao']} \n"
        await ctx.send(resposta)

    @commands.command(name="anote")
    async def anote(self, ctx):
        """Cria um lembrete"""
        await ctx.send("📝 O que você quer que eu te lembre?")
        def check(m): return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg_lembrar = await self.bot.wait_for("message", timeout=60, check=check)
            conteudo = msg_lembrar.content.strip()

            await ctx.send("⏰ Quando? (formato `DD/MM/AAAA HH:MM` ou `diario HH:MM` ou `semanal DIA HH:MM`)\nExemplos:\n`05/08/2025 19:30`\n`diario 08:00`\n`semanal segunda 18:00`")
            msg_quando = await self.bot.wait_for("message", timeout=60, check=check)
            info = msg_quando.content.lower().strip()

            canal_id = ctx.channel.id
            autor_id = ctx.author.id
            scheduler = get_scheduler()

            if info.startswith("diario "):
                hora = datetime.strptime(info.split(" ")[1], "%H:%M").time()
                scheduler.add_job(
                    lambda: self.bot.loop.create_task(
                        self.bot.get_channel(canal_id).send(f"⏰ <@{autor_id}> lembrete diário: {conteudo}")
                    ),
                    trigger="cron", hour=hora.hour, minute=hora.minute
                )
                await ctx.send("✅ Ta feito chefia")

            elif info.startswith("semanal "):
                partes = info.split(" ")
                dia_semana = partes[1]
                hora = datetime.strptime(partes[2], "%H:%M").time()
                dias = {
                    "segunda": "mon", "terça": "tue", "quarta": "wed",
                    "quinta": "thu", "sexta": "fri", "sábado": "sat", "domingo": "sun"
                }
                if dia_semana not in dias:
                    return await ctx.send(" é pra escrever dia de semana o imbecil.")
                scheduler.add_job(
                    lambda: self.bot.loop.create_task(
                        self.bot.get_channel(canal_id).send(f"📆 <@{autor_id}> lembrete semanal ({dia_semana}): {conteudo}")
                    ),
                    trigger="cron", day_of_week=dias[dia_semana], hour=hora.hour, minute=hora.minute
                )
                await ctx.send("✅ Ta feito chefia")

            else:
                data = datetime.strptime(info, "%d/%m/%Y %H:%M")
                scheduler.add_job(
                    lambda: self.bot.loop.create_task(
                        self.bot.get_channel(canal_id).send(f"🔔 <@{autor_id}> lembrete: {conteudo}")
                    ),
                    trigger="date", run_date=data
                )
                await ctx.send("✅ Ta feito chefia ")

        except Exception as e:
            await ctx.send("❌ Erro ao configurar lembrete. Verifique o formato e tente novamente.")
            print(f"[ERRO] anote: {e}")

def setup(bot):
    bot.add_cog(Agenda(bot))