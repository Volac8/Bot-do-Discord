from discord.ext import commands
import asyncio
import importlib
import openai
import re
import ast

ID_PERMITIDO = [442462428748447755, 561686139581497375, 337276446911496192, 622645792221691905, 327258575858565120]

def usuario_tem_permissao(ctx):
    return any(c.id in ID_PERMITIDO for c in ctx.author.id)

def comando_ja_existe(nome):
    with open("comandos.py", "r", encoding="utf-8") as f:
        return f"async def {nome}(" in f.read()

def validar_ast_comando(codigo: str):
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as e:
        raise ValueError("Erro de sintaxe no código gerado.") from e

    funcs = [n for n in ast.walk(arvore) if isinstance(n, ast.AsyncFunctionDef)]

    if len(funcs) != 1:
        raise ValueError("O código deve conter exatamente um método async.")

    func = funcs[0]
    args = [a.arg for a in func.args.args]

    if "self" not in args or "ctx" not in args:
        raise ValueError("O método precisa receber self e ctx.")

def corrigir_assinatura(codigo: str):
    linhas = codigo.splitlines()
    novas = []

    for linha in linhas:
        if linha.strip().startswith("async def"):
            # Extrai nome e argumentos
            match = re.match(r"\s*async def (\w+)\((.*?)\):", linha)
            if not match:
                raise ValueError("Assinatura inválida.")

            nome, args = match.groups()
            args = [a.strip() for a in args.split(",") if a.strip()]

            # Garante self
            if not args or args[0] != "self":
                args.insert(0, "self")

            # Garante ctx
            if "ctx" not in args:
                args.insert(1, "ctx")

            nova_linha = f"    async def {nome}({', '.join(args)}):"
            novas.append(nova_linha)
        else:
            novas.append("    " + linha if linha.strip() else linha)

    return "\n".join(novas)

def limpar_markdown(codigo: str):
    """Remove blocos de código markdown."""
    # Remove blocos com ``` python ou ```
    codigo = re.sub(r'^```python\n', '', codigo, flags=re.MULTILINE)
    codigo = re.sub(r'^```\n', '', codigo, flags=re.MULTILINE)
    codigo = re.sub(r'\n```$', '', codigo, flags=re.MULTILINE)
    return codigo.strip()

def identar_codigo(codigo:str, espacos=4):
    linhas = codigo.splitlines()
    return "\n".join((" " * espacos + l if l.strip() else l) for l in linhas)

def adicionar_comando_seguro(arquivo: str, codigo: str):
    """Adiciona código ao arquivo de forma segura, validando o resultado."""
    with open(arquivo, "r", encoding="utf-8") as f:
        conteudo_atual = f.read()
    
    # Garante que o arquivo termina com newline
    if conteudo_atual and not conteudo_atual.endswith("\n"):
        conteudo_atual += "\n"
    
    # Adiciona o novo código com espaçamento
    conteudo_novo = conteudo_atual + "\n\n" + codigo
    
    # Valida a sintaxe do arquivo resultante
    try:
        ast.parse(conteudo_novo)
    except SyntaxError as e:
        raise ValueError(f"Sintaxe inválida no arquivo após adicionar código: {e}") from e
    
    # Escreve de volta
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo_novo)

class Evolucao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="evolua")
    async def criarcomando(self, ctx):

        if not usuario_tem_permissao(ctx):
            return await ctx.send("Quem você acha que é para mandar em mim?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Claro meu senhor, qual será o **nome** do novo comando?")
        nome_msg = await self.bot.wait_for("message", timeout=60, check=check)
        nome_cmd = nome_msg.content.strip().lower()

        if comando_ja_existe(nome_cmd):
            return await ctx.send("Esse comando já existe. Apague-o da realidade com 'desevolua' antes.")

        await ctx.send(f"O que o comando `{nome_cmd}` deve fazer?")
        desc_msg = await self.bot.wait_for("message", timeout=300, check=check)
        descricao = desc_msg.content.strip()

        await ctx.send("**Sons de evolução**")
        prompt = (
            f"Gere APENAS o código Python, SEM explicações, SEM markdown, SEM blocos de código.\n"
            f"Regras obrigatórias:\n"
            f"1. NÃO use ``` ou blocos de código\n"
            f"2. NÃO use imports\n"
            f"3. Use EXATAMENTE 4 espaços de indentação\n"
            f"4. Escreva um método async de uma Cog discord.py\n"
            f"5. Use @commands.command(name=\"{nome_cmd}\")\n"
            f"6. O método DEVE receber (self, ctx) como argumentos\n"
            f"\n"
            f"Comando: {nome_cmd}\n"
            f"Funcionalidade: {descricao}\n"
            f"\n"
            f"Responda APENAS com o código, começando com @commands.command"
        )

        resp = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )

        codigo = resp.choices[0].message.content
        codigo = limpar_markdown(codigo)
        codigo = corrigir_assinatura(codigo)
        #validar_ast_comando(codigo)

        adicionar_comando_seguro("comandos.py", codigo)

        try:
            await self.bot.reload_extension("comandos")
            await ctx.send(f"Suas ordens são absolutas senhor, o comando `{nome_cmd}` foi criado e carregado com sucesso.")
            await ctx.send("Código gerado:\n```python\n" + identar_codigo(codigo) + "\n```")
        except Exception as e:
            await ctx.send("O corpo falhou na adaptação.")
            print(e)

    @commands.command(name="desevolua")
    async def remover_comando(self, ctx, nome: str):

        if not usuario_tem_permissao(ctx):
            return await ctx.send("Quem você acha que é para mandar em mim?")
            
        nome = nome.lower()
        arquivo = "comandos.py"

        with open(arquivo, "r", encoding="utf-8") as f:
            linhas = f.readlines()

        novo = []
        i = 0
        removido = False

        while i < len(linhas):
            linha = linhas[i]
            stripped = linha.lstrip()

            # Detecta async def do comando
            if stripped.startswith(f"async def {nome}("):
                removido = True

                # Remove decorator imediatamente acima, se existir
                if novo and novo[-1].lstrip().startswith("@commands.command"):
                    novo.pop()

                # Pula todo o bloco do método
                indent = len(linha) - len(stripped)
                i += 1
                while i < len(linhas):
                    prox = linhas[i]
                    if prox.strip() and (len(prox) - len(prox.lstrip())) <= indent:
                        break
                    i += 1
                continue

            novo.append(linha)
            i += 1

        if not removido:
            return await ctx.send("Esse comando não existe no corpo.")

        with open(arquivo, "w", encoding="utf-8") as f:
            f.writelines(novo)

        await self.bot.reload_extension("comandos")
        await ctx.send(f"O comando `{nome}` foi reduzido a uma ameba com sucesso.")

async def setup(bot):
    await bot.add_cog(Evolucao(bot))
