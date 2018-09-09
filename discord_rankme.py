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

bot = commands.Bot(command_prefix=set_prefix)

@bot.event
async def on_ready():
    print("Bot connected!\nCurrently linked to {}\nThis bot was created by Weeb.Network".format(bot.user.name)) #Prints bots status and what bot token its connect to.

@bot.command(pass_context=True)
async def stats(ctx, steam_id):
    try:
        cusrorType = pymysql.cursors.DictCursor
        connectionObject = pymysql.connect(host=db_ip, user=db_user, password=db_pass, db=db_name, charset=charSet,cursorclass=cusrorType,autocommit=True)

        cursorObject = connectionObject.cursor()

        r = requests.get('https://steamid.eu/api/convert.php?api={}&input={}&format=json'.format(steamid_api,steam_id))
        data =r.json()
        converter = data["converted"]

        steam_replace = converter["steamid"]

        steam_replace = steam_replace[:7].replace('0', '1') + steam_replace[7:]

        sqlQuery = "select rounds_tr, rounds_ct, kills, deaths, hits, shots, headshots, name, score from {} where steam = '{}' limit 1".format(table_name,steam_replace)
        cursorObject.execute(sqlQuery)
        rows = cursorObject.fetchall()

        for row in rows:
            total_rounds = row["rounds_tr"] + row["rounds_ct"]
            kdr = Decimal(row["kills"] / row["deaths"])
            hit_percentage_clac = row["hits"]/row["shots"]
            hit_percentage = Decimal(hit_percentage_clac*100)
            headshot_percentage_clac = row["headshots"]/row["kills"]
            headshot_percentage = Decimal(headshot_percentage_clac*100)
            kdr_roundup = round(kdr,2)
            headshot_roundup = round(headshot_percentage,2)
            hit_roundup = round(hit_percentage,2)

            embed = discord.Embed(title="**Rankme statistics for {}**".format(row["name"]), colour=discord.Colour(embed_color), description="\n**Score:** {}\n**KDR:** {}\n**Hits Percentage:** {}%\n**Headshot Percentage:** {}%\n**Kills:** {}\n**Deaths:** {}\n**Shots:** {}\n**Hits:** {}\n**Total Rounds Played:** {}".format(row["score"],kdr_roundup,hit_roundup,headshot_roundup,row["kills"],row["deaths"],row["shots"],row["hits"],total_rounds))
            await bot.say(embed=embed)
        
        cursorObject.close()
    except:
        embed = discord.Embed(colour=discord.Colour(embed_color), description="**Please input a invalid Steam ID!**")
        await bot.say(embed=embed)

@bot.command(pass_context=True)
async def top(ctx):
    cusrorType = pymysql.cursors.DictCursor
    connectionObject = pymysql.connect(host=db_ip, user=db_user, password=db_pass, db=db_name, charset=charSet,cursorclass=cusrorType,autocommit=True)
    
    cursorObject = connectionObject.cursor()

    counter = 0
    description = ""

    sqlQuery = "select name, score from {} order by score desc limit 20".format(table_name)
    cursorObject.execute(sqlQuery)
    rows = cursorObject.fetchall()

    for row in rows:
        counter += 1
        description += "**{}.** {} **|** Score: {}\n".format(counter, row["name"], row["score"])

    embed = discord.Embed(title="**Top 20 Players**", colour=discord.Colour(embed_color), description="{}".format(description))
    await bot.say(embed=embed)

    cursorObject.close()


bot.run(bot_token)
