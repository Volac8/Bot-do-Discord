# 📋 Guia de Refatoração - Estrutura Nova

## ✅ O que foi feito:

### 1. **utils.py** (criado)
Centraliza todas as funções utilitárias:
- Gerenciamento de agenda (`carregar_agenda()`, `salvar_agenda()`)
- Gerenciamento de duelos (`carregar_duelos()`, `registrar_vitoria()`)
- Histórico de conversa (`adicionar_mensagem()`, `obter_conversa()`)
- Scheduler de lembretes (`agendar_notificacoes()`, `init_scheduler()`)

### 2. **core.py** (atualizado)
Eventos globais do bot:
- `on_ready()`: Inicializa scheduler e reagenda eventos ao reiniciar
- `on_message()`: Registra mensagens no histórico e processa comandos

### 3. **comandos_personalizados.py** (refatorado)
Todos os comandos agora em um único Cog:

**Comandos de Duelo:**
- `eu` - Inicia duelo entre dois participantes
- `rankduelos` - Mostra ranking

**Comandos de Humor:**
- `desgoze` - Desgoza calças
- `amoleça` - Amolece pinto
- `here` - Turururu
- `amaldiçoe` - Amaldiçoa alguém
- `xingue` - Xinga alguém

**Comandos de IA (com OpenAI):**
- `defina` - Define um termo
- `defenda-me` - Defende você em um debate
- `resumir` - Resume conversa

**Comandos de Agenda RPG:**
- `agendar` - Agenda um RPG
- `listar` - Lista RPGs agendados
- `excluir` - Exclui um RPG
- `agendados` - Mostra todos os RPGs
- `anote` - Cria lembretes (diário, semanal, único)

### 4. **setup.py** (já estava certo)
Carrega as extensões automaticamente

---

## 🔄 Fluxo de dados:

```
main.py
  ↓
setup.py (setup_bot)
  ↓
├─ core.py (register_events) → on_ready, on_message
└─ comandos_personalizados.py (extension) → todos os comandos
  ↓
utils.py (funções compartilhadas)
```

---

## 🚀 Como funciona:

1. **main.py** inicia o bot
2. **setup.py** é chamado e:
   - Registra eventos via `core.py`
   - Carrega extensões (cogs)
3. **comandos_personalizados.py** é uma Cog que contém todos os comandos
4. Todos compartilham funções via **utils.py**

---

## 📝 Notas importantes:

- ✅ Agenda é recarregada automaticamente ao reiniciar
- ✅ Scheduler mantém lembretes funcionando
- ✅ Histórico de conversa persiste em memória
- ✅ Todos os comandos estão concentrados em um lugar
- ⚠️ Lembretes e agendamentos são perdidos ao reiniciar (use database em produção)

---

## 🔧 Próximos passos (opcional):

Se quiser melhorar ainda mais:
1. Mover `evolucao.py` para o mesmo padrão
2. Usar banco de dados (MongoDB/SQLite) em vez de JSON
3. Dividir comandos em múltiplos cogs (um para duelos, outro para agenda, etc.)
4. Adicionar validação de permissões mais robusta
