import importlib, sys

# Módulos que podem ser recarregados (ordem importa!)
RECARREGAVEIS = [
    "utils",          # Deve vir primeiro pois é importado por outros
    "setup",
    "reload_utils"
]

async def reload_manual(bot):
    """
    Recarrega todas as extensões (cogs) e módulos do bot sem reiniciar.
    Retorna (lista_sucesso, lista_falha)
    """
    sucesso = []
    falha = []

    print("🔄 [RELOAD] Iniciando hot-reload...")

    # 1️⃣ Primeiro recarrega módulos compartilhados (ordem importa!)
    print("   Recarregando módulos base...")
    modulos_recarregados = {}
    
    for nome in RECARREGAVEIS:
        if nome in sys.modules:
            try:
                print(f"   ↻ {nome}...", end=" ")
                modulo = sys.modules[nome]
                modulo_recarregado = importlib.reload(modulo)
                modulos_recarregados[nome] = modulo_recarregado
                sucesso.append(nome)
                print("✓")
            except Exception as e:
                print(f"✗")
                print(f"      Erro: {str(e)}")
                falha.append((nome, str(e)))
        else:
            print(f"   ⚠ {nome} não está em sys.modules (pulando)")

    # 2️⃣ Depois recarrega extensões (que usam os módulos acima)
    print("   Recarregando extensões...")
    for ext in list(bot.extensions.keys()):
        try:
            print(f"   ↻ {ext}...", end=" ")
            await bot.reload_extension(ext)
            sucesso.append(ext)
            print("✓")
        except Exception as e:
            print(f"✗")
            print(f"      Erro: {str(e)}")
            falha.append((ext, str(e)))

    print("✅ [RELOAD] Hot-reload concluído!\n")
    return sucesso, falha
