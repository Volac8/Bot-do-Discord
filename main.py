from datetime import datetime
from discord.ext import commands
import openai, discord, utils.utils as utils, os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

class Jarvis(commands.Bot):
    def __init__(self):
        """initialize bot object"""
        self.config = utils.get_config()
        super().__init__(
            command_prefix = commands.when_mentioned_or(*self.config["prefixes"]),
            case_insensitive = True,
            intents = discord.Intents.all()
        )
        self.remove_command("help")
        self.load_extensions()

    def load_extensions(self):
        """at initialization, load all cogs"""
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                self.load_extension(f"cogs.{file[:-3]}") # type: ignore

    async def is_owner(self, user:discord.abc.User):
        """override `is_owner` check so all managers can use `jsk`"""
        if user.id in self.config["managers"]:
            return True  # managers have owner permissions

        return await super().is_owner(user)

    async def on_ready(self):
        from utils.utils import init_scheduler, carregar_agenda, agendar_notificacoes
        print(f"🤖 Bot online como {self.user}")
        
        init_scheduler()
        agenda_rpg = carregar_agenda()
        for chave, item in agenda_rpg.items():
            dt = datetime.strptime(chave, "%d/%m/%Y %H:%M")
            if dt > datetime.now():
                agendar_notificacoes(bot, dt, item["canal_id"], item["cargo_id"], item["descricao"], item["duracao_min"])
        
        
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{self.config['prefixes'][0]}help")
        await self.change_presence(status=discord.Status.dnd, activity=activity)

if __name__ == "__main__":
    bot = Jarvis()
    openai.api_key = bot.config["api_key"]
    bot.run(bot.config["token"])
