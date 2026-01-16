from main import bot
import discord, main, importlib

@bot.command()
async def piada(ctx):
    piadas = [
        "Por que o livro foi ao médico? Porque tinha muitas páginas doentes!",
        "O que o pato falou para a pata? Vem Quá!",
        "Por que o computador foi ao médico? Porque estava com vírus!",
        "Qual é o peixe mais inteligente? O peixe-papagaio!",
        "Por que a galinha atravessou a rua? Para chegar do outro lado!"
    ]
    import random
    await ctx.send(random.choice(piadas))

@bot.command()
async def dados(ctx):
    import random
    resultado = random.randint(1, 6)
    await ctx.send(f'Você rolou um dado e obteve: {resultado}')

@bot.command()
async def moggar(ctx, member: discord.Member):
    await ctx.send(f"{member.mention} você é um idiota!")

@bot.command()
async def recarregar(ctx):
    importlib.reload(main)
    await ctx.send(f"Fui atualizado :D")

@bot.command()
async def suportar(ctx):
    await ctx.send("Suportar o peso de todas as verdades.")

@bot.command()
async def suporte(ctx):
    await ctx.send("Suportei o peso de todas as verdades com sucesso!")

@bot.command()
async def reload(ctx):
    await ctx.send("Reloading bot...")
    await bot.reload_extension('comandos_personalizados')  # Substitua 'cog_name' pelo nome da sua extensão


@bot.command()
async def ofenda(ctx, member: discord.Member):
    await ctx.send(f"{member.mention} sinta-se ofendido!")