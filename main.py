from discord.ext import commands
import openai, setup, discord, os, dotenv
from pathlib import Path

# ✅ Carrega .env ANTES de tudo
dotenv_path = Path(__file__).parent / ".env"
dotenv.load_dotenv(dotenv_path)

# ✅ Verifica se as variáveis foram carregadas
discord_token = os.getenv("DISCORD_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not discord_token:
    raise ValueError("❌ DISCORD_TOKEN não encontrado em .env!")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY não encontrado em .env!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

class Jarvis(commands.Bot):
    async def setup_hook(self):
        """Executado antes do bot ficar online"""
        await setup.setup_bot(self)

bot = Jarvis(command_prefix="Jarvis, ", intents=intents)

openai.api_key = openai_api_key
bot.run(discord_token)
