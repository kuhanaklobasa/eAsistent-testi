# Primer uporabe knjižnice v kombinaciji z discord.py

import discord
from reactionmenu import ReactionButton, ReactionMenu, errors
from discord.ext import commands
import easistent_testi as testi

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

testi_client = testi.TestiClient("uporabnik", "geslo")

@client.command()
async def testi(ctx: commands.Context, predmet: str=None, mesec:str=None):
    redovalnica = testi_client.izdelajRedovalnico()
    if predmet:
        testi = redovalnica.filtriraj("predmet", lambda x, y: y in x, predmet)
    if mesec:
        testi = redovalnica.filtriraj("datetime", lambda x, y: x.month == y, mesec)
    else:
        testi = redovalnica.testi
    menu = ReactionMenu(ctx, menu_type=ReactionMenu.TypeEmbedDynamic, rows_requested=3)
    menu.add_button(ReactionButton.back())
    menu.add_button(ReactionButton.next())

    for test in testi:
        menu.add_row(
            f"""predmet: {test.predmet}\nopis: {test.opis}\ndatum in ura: {test.datetime}\n```ansi\n[2;31m------------------------[0m```""",
        )
    try:
        await menu.start()
    except errors.NoPages:
        await ctx.send("Ni testov", ephemeral=True)

client.run("ODU0NDExMDg3ODM4MzE0NDk2.GzcSUb.euOdXtZrarNNh0Nt5gs_a78JoA_4YGls228fv8")