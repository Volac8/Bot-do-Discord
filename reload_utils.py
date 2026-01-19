import importlib, sys
from discord.ext import commands

RECARREGAVEIS = [
    "setup",
    "core",
    "reload_utils"
]

async def reload_manual(bot):
    sucesso = []
    falha = []

    # extensões
    for ext in list(bot.extensions.keys()):
        try:
            await bot.reload_extension(ext)
            sucesso.append(ext)
        except Exception as e:
            falha.append((ext, str(e)))

    # módulos do "main"
    for nome in RECARREGAVEIS:
        if nome in sys.modules:
            try:
                importlib.reload(sys.modules[nome])
                sucesso.append(nome)
            except Exception as e:
                falha.append((nome, str(e)))

    return sucesso, falha
