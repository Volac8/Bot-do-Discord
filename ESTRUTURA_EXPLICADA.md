# 🤖 Estrutura do Bot Discord - Visualização

```
Bot-do-Discord/
│
├── main.py                      # Entrada do bot (simples)
│   └── Apenas inicializa o bot
│
├── setup.py                     # Configuração
│   └── Carrega extensões e eventos
│
├── core.py                      # Eventos globais
│   ├── @bot.event on_ready()     # Inicializa scheduler
│   └── @bot.event on_message()   # Registra mensagens
│
├── comandos_personalizados.py   # TODOS OS COMANDOS (Cog)
│   ├── Duelos (eu, rankduelos)
│   ├── Humor (desgoze, amoleça, here, amaldiçoe, xingue)
│   ├── IA (defina, defenda-me, resumir)
│   └── Agenda (agendar, listar, excluir, agendados, anote)
│
├── evolucao.py                  # Extensão de evolução (existente)
│
├── utils.py                     # Funções compartilhadas ⭐ NOVO
│   ├── Gestão de agenda
│   ├── Gestão de duelos
│   ├── Histórico de conversa
│   └── Scheduler e notificações
│
├── reload_utils.py              # Sistema de reload
│
├── agenda_rpg.json              # Dados de agenda (persistente)
├── duelos.json                  # Dados de duelos (persistente)
├── peticoes_eliminar.json       # Dados de petições
└── __pycache__/                 # Cache Python
```

---

## 🔀 Fluxo de Execução

### 1️⃣ Inicialização (Startup)
```
bot.run() em main.py
    ↓
setup.setup_bot(bot)
    ↓
├─ core.register_events(bot)
│   ├─ @bot.event on_ready
│   │   ├─ init_scheduler()
│   │   └─ reagendar eventos antigos
│   └─ @bot.event on_message
│
└─ bot.load_extension("comandos_personalizados")
    ├─ ComandosPersonalizados(bot)
    └─ Todos os comandos prontos
```

### 2️⃣ Uso de Comando (Runtime)
```
Usuário: "Jarvis, eu"
    ↓
Discord bot recebe mensagem
    ↓
@bot.event on_message() em core.py
    ├─ adicionar_mensagem() [de utils.py]
    └─ bot.process_commands()
        ↓
    @commands.command("eu") em comandos_personalizados.py
        ├─ Iniciar duelo
        ├─ Chamar avaliar_duelo()
        └─ registrar_vitoria() [de utils.py]
```

### 3️⃣ Uso de Dados
```
Arquivo JSON ←→ utils.py ←→ comandos_personalizados.py
                            (e outros módulos)
```

---

## 📦 Exemplo: Comando de Agenda

```python
# Em comandos_personalizados.py
@commands.command(name="agendar")
async def agendar(self, ctx):
    # Pede data/hora
    # Valida conflitos
    # Salva em self.agenda_rpg
    salvar_agenda()  # ← Chama função em utils.py
    agendar_notificacoes(self.bot, data, canal_id, cargo_id, descricao, dur_min)
    # ↑ Também de utils.py - cria jobs no scheduler
```

---

## 🎯 Benefícios da Nova Estrutura

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Organização** | Tudo em um arquivo comentado | Separado em módulos |
| **Reuso de código** | Duplicado | Centralizado em utils.py |
| **Manutenção** | Difícil | Fácil |
| **Escalabilidade** | Limitada | Pode adicionar mais cogs |
| **Debugging** | Complexo | Rastreável por módulo |

---

## 🔧 Passo a Passo: Adicionar Novo Comando

### Opção 1: Adicionar ao Cog existente
```python
# Em comandos_personalizados.py, dentro de ComandosPersonalizados
@commands.command(name="novo")
async def novo_comando(self, ctx):
    await ctx.send("Novo comando!")
```

### Opção 2: Criar novo Cog (extensão separada)
```python
# novo_modulo.py
from discord.ext import commands

async def setup(bot):
    await bot.add_cog(NovoModulo(bot))

class NovoModulo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="outro")
    async def outro_comando(self, ctx):
        await ctx.send("Outro comando!")
```

```python
# Em setup.py
extensoes = [
    "comandos_personalizados",
    "evolucao",
    "novo_modulo"  # ← Adicione aqui
]
```

---

## ⚡ Performance

- ✅ Carregamento rápido (não carrega tudo)
- ✅ Menos memória (modular)
- ✅ Scheduler eficiente (APScheduler)
- ✅ Eventos otimizados

---

## 📌 Checklist de Verificação

- [x] Todos os comandos do código antigo estão em `comandos_personalizados.py`
- [x] Todos os eventos estão em `core.py`
- [x] Funções compartilhadas estão em `utils.py`
- [x] Scheduler é inicializado em `on_ready()`
- [x] Histórico de conversa funciona em `on_message()`
- [x] Agenda é salva e carregada corretamente
- [x] Duelos são registrados
- [x] Lembretes são agendados

🎉 **Tudo pronto para usar!**
