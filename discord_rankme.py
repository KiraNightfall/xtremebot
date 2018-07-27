import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Bot
import asyncio
import pymysql
import requests
import json
from decimal import Decimal

###################################################################################################################################################################
#Config
db_ip = ""
db_user = ""
db_pass = ""
db_name = ""
charSet = "utf8mb4"
table_name = "rankme"

steamid_api = "" #https://steamid.eu/my_api_manager.php

bot_token = "" #Discord bot token. Find at https://discordapp.com/developers/applications/me
set_prefix = '!' #Sets command prefix.

embed_color = 0xE8CA11   #Do not remove 0x  || Message Color. Hex, 6 characters. Do NOT include # | Helpful link https://htmlcolorcodes.com/color-picker/
###################################################################################################################################################################

cusrorType = pymysql.cursors.DictCursor
connectionObject = pymysql.connect(host=db_ip, user=db_user, password=db_pass, db=db_name, charset=charSet,cursorclass=cusrorType,autocommit=True)

cursorObject = connectionObject.cursor()

bot = commands.Bot(command_prefix=set_prefix)

@bot.event
async def on_ready():
    print("Bot connected!\nCurrently linked to {}\nThis bot was created by Weeb.Network".format(bot.user.name)) #Prints bots status and what bot token its connect to.

@bot.command(pass_context=True)
async def stats(ctx, steam_id):
    try:
        r = requests.get('https://steamid.eu/api/convert.php?api={}&input={}&format=json'.format(steamid_api,steam_id))
        data =r.json()
        converter = data["converted"]

        steam_replace = converter["steamid"]

        steam_replace = steam_replace[:7].replace('0', '1') + steam_replace[7:]

        sqlQuery = "select * from {} where steam = '{}'".format(table_name,steam_replace)
        cursorObject.execute(sqlQuery)
        rows = cursorObject.fetchall()

        for row in rows:
            total_rounds = row["rounds_tr"] + row["rounds_ct"]
            kdr = Decimal(row["kills"] / row["deaths"])
            hit_percentage = row["shots"]%row["hits"]/100
            headshot_percentage = row["kills"]%row["headshots"]
            kdr_roundup = round(kdr,2)

            embed = discord.Embed(title="**Rankme statistics for {}**".format(row["name"]), colour=discord.Colour(embed_color), description="\n**Score:** {}\n**KDR:** {}\n**Hits Percentage:** {}%\n**Headshot Percentage:** {}%\n**Kills:** {}\n**Deaths:** {}\n**Shots:** {}\n**Hits:** {}\n**Total Rounds Played:** {}".format(row["score"],kdr_roundup,hit_percentage,headshot_percentage,row["kills"],row["deaths"],row["shots"],row["hits"],total_rounds))
            await bot.say(embed=embed)
    except:
        embed = discord.Embed(colour=discord.Colour(embed_color), description="**Please input a invalid Steam ID!**")
        await bot.say(embed=embed)

bot.run(bot_token)