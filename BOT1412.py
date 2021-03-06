import discord
from discord.ext import commands
import dropsims
from Roles import allowed_roles
from dropsims import tob
import json
from Token import DISCORD_TOKEN
from fractions import Fraction
import pkgutil
import importlib
import probabilityFlavourText
from Zebt import Zebt
import TTM

_zebt = Zebt()
bot = commands.Bot(command_prefix="!")

@bot.command()
async def zebt(ctx, name: str, name_2 = None, amount = None):
    """Manage zebts
    Syntax:
        !zebt name
        !zebt name_owes name_owed +amount
        !zebt name_owes name_owed -amount
        !zebt name_owes name_owed amount
    Without +- specifiers, the debt will be directly replaced by the new amount"""
    if name_2 is None:
        zebt_owed, zebt_owes = _zebt.zebt_list
        owed_dict = None
        owes_dict = None
        if name in zebt_owed:
            owed_dict = zebt_owed[name]
        if name in zebt_owes:
            owes_dict = zebt_owes[name]
        response_str = ""
        if owed_dict is not None:
            response_str += name + " owes:"
            for owed_name in owed_dict.keys():
                response_str += "\n\t" + owed_name + " " + '{:,}gp'.format(owed_dict[owed_name])
        if owes_dict is not None:
            if len(response_str):
                response_str += "\n"
            response_str += name + " is owed:"
            for owes_name in owes_dict.keys():
                response_str += "\n\t" + owes_name + " " + '{:,}gp'.format(owes_dict[owes_name])
        if len(response_str):
            await ctx.send(response_str)
        else:
            await ctx.send(name + " is owed and owes nothing!")
    else:
        _zebt.update_zebt(name, name_2, amount)
        zebt_owed, zebt_owes = _zebt.zebt_list
        owed = 0
        if name in zebt_owed:
            if name_2 in zebt_owed[name]:
                owed = zebt_owed[name][name_2]
        await ctx.send("Zebt updated, " + name + " now owes " + name_2 + ": " + '{:,}gp'.format(owed))

MAX_FILE_SIZE = 10 ** 7
@bot.command()
async def ttm(ctx, arg1, arg2 = "EHP", arg3 = "Main"):
    """Check your TTM with custom, saved xp rates
    Syntax to check rates: 
        !ttm user_name @owner rates_name
    Syntax to upload rates (just attach a file and enter the command in the text field):
        !ttm rates_name
    Example of upload and rate check:
        !ttm my_rates
        !ttm my_osrs_name @my_discord_handle my_rates
    Each person can upload their own custom rates rather than just EHP rates
    These rates are associated with the uploader's discord account
    The rates are accessed directly from discord, if you delete the attachment, the rates are lost
    Hence when accessing, you specify the person and the xp list that they have collected
    EHP rates can be accessed by the following commands, main EHP is used be default:
        !ttm user_name EHP Main
    EHP rates currently only exist for mains.
    Rate files must be in JSON format.
    The format of the Main EHP rates can be seen here:
        https://cdn.discordapp.com/attachments/553676760357535745/702999634074665050/main_ehp.json 
    """
    if len(ctx.message.attachments):
        file = ctx.message.attachments[0]
        TTM.add_rate(file.url, str(ctx.author.id), arg1.lower())
        await ctx.send("Rates successfully added.")
    else:
        if arg2 != "EHP":
            arg2 = arg2[3:-1]
        how_to_train, ttm = TTM.get_ttm(arg1, arg2.lower(), arg3.lower())
        embed = discord.Embed(description="Time required for each skilling method to max (in hours)")
        embed.title = "Time to max for " + arg1
        maxed = True
        for method, time in how_to_train.items():
            if time > 0:
                maxed = False
                embed.add_field(name=method, value=str(time), inline=True)
        if maxed:
            embed.add_field(name="Anything", value="0, you're already maxed!")
        embed.set_footer(text="Time to max: " + str(ttm))
        await ctx.send(embed=embed)

@bot.command()
async def tt200m(ctx, arg1, arg2 = "EHP", arg3 = "Main"):
    """Check your TTM with custom, saved xp rates
    Syntax to check rates: 
        !ttm user_name @owner rates_name
    Syntax to upload rates (just attach a file and enter the command in the text field):
        !ttm rates_name
    Example of upload and rate check:
        !ttm my_rates
        !ttm my_osrs_name @my_discord_handle my_rates
    Each person can upload their own custom rates rather than just EHP rates
    These rates are associated with the uploader's discord account
    The rates are accessed directly from discord, if you delete the attachment, the rates are lost
    Hence when accessing, you specify the person and the xp list that they have collected
    EHP rates can be accessed by the following commands, main EHP is used be default:
        !ttm user_name EHP Main
    EHP rates currently only exist for mains.
    Rate files must be in JSON format.
    The format of the Main EHP rates can be seen here:
        https://cdn.discordapp.com/attachments/553676760357535745/702999634074665050/main_ehp.json 
    """
    if len(ctx.message.attachments):
        file = ctx.message.attachments[0]
        TTM.add_rate(file.url, str(ctx.author.id), arg1.lower())
        await ctx.send("Rates successfully added.")
    else:
        if arg2 != "EHP":
            arg2 = arg2[3:-1]
        how_to_train, ttm = TTM.get_tt200m(arg1, arg2.lower(), arg3.lower())
        embed = discord.Embed(description="Time required for each skilling method to 200m xp (in hours)")
        embed.title = "Time to 200m for " + arg1
        maxed = True
        for method, time in how_to_train.items():
            if time > 0:
                maxed = False
                embed.add_field(name=method, value=str(time), inline=True)
        if maxed:
            embed.add_field(name="Anything", value="0, you're already 200m!")
        embed.set_footer(text="Time to 200m: " + str(ttm))
        await ctx.send(embed=embed)

@bot.command()
async def finish(ctx, name: str, trials = 1, extraArg1 = "True", extraArg2 = "False"):
    """Simulates the completion of an activity the requested amount of times and outputs empirical data about the sample.
    Syntax: 
        !finish activity ?trialcount ?*ignoretrash
        !finish tob ?trialcount ?teamsize ?*mvpallrooms
    parameters:
        activity - The activity to simulate (bandos, corp,.. See !activities)
        trialcount - The amount of times to complete the activity (finish getting all items once)
        ignoretrash - Whether to exclude the drops generally considered trash (jars, etc)
        mvpallrooms - To keep input brief, we assume you're either always mvp or never mvp, see https://twitter.com/jagexkieren/status/1145376451446751232?lang=en
    
    Note: ? denotes optional. * denotes boolean (True or False, case sensitive))"""

    if trials > 10000:
        await ctx.send("I like to actually use my PC, prick, 10k completions for you. If you tried Zulrah then double fuck you, my PC weeps.")
        trials = 10000
    elif trials < 1:
        trials = 1
    averageKC = 0
    averageItemKCs = {}
    averageItemsFound = {}
    title = ""
    description = "The average amount of each item obtained during completion, as well as the average KC to first see each item."
    embed = discord.Embed(description=description)
    async with ctx.typing():
        if name.lower() == "tob":
            if extraArg1 == "True":
                extraArg1 = "4"
            title = "Simulation of " + str(trials) + " Theatre of Blood completions, with a team size of " + extraArg1
            if extraArg2 == "False":
                title += ", where you do not get MvP in any room"
            else: 
                title += ", where you get MvP in every room"
            averageKC, averageItemKCs, averageItemsFound, trashDrops = tob.simulate(trials, int(extraArg1), extraArg2 == "True")
        else:
            title = "Simulation of " + str(trials) + " " + name + " completions"
            averageKC, averageItemKCs, averageItemsFound, trashDrops = dropsims.simulate(name, trials, extraArg1 == "True")
        for itemName in averageItemKCs.keys():
            empiricalRate = averageItemsFound[itemName] / averageKC
            empiricalRateFrac = Fraction(empiricalRate).limit_denominator(100000)
            empiricalRateFracSimplified = Fraction(1, round(empiricalRateFrac.denominator / empiricalRateFrac.numerator))
            embed.add_field(name=itemName, value="Amount: " + str(averageItemsFound[itemName]) + "\nFirst seen: " + str(averageItemKCs[itemName]) + \
                "\nEmpirical rate: " + str(empiricalRateFracSimplified))
        footer = "Average completion KC: " + str(averageKC)
        if extraArg1 == "True" and len(trashDrops) > 0:
            footer = footer + "\nIgnored drops: " + str(trashDrops)
        embed.set_footer(text=footer)
    embed.title = title
    await ctx.send(embed=embed)    

@finish.error
async def finish_error(ctx, error):
    await ctx.send("Invalid !finish arguments.\nSyntax: \n\t!finish name trials ignoretrash\n\t" \
        + "!finish tob trials teamsize mvpallrooms\n" + str(error))
    print(error)

@bot.command()
async def stop(ctx):
    await bot.logout()

@bot.command()
async def role(ctx, role: discord.Role = None):
    """Toggle a discord role on or off."""
    if role is None:
        await ctx.send("List of assignable roles: " + str(allowed_roles))
    if role.name in allowed_roles:
        if not role in ctx.message.author.roles:
            await ctx.message.author.add_roles(role)
            await ctx.send("Role added.")
        else:
            await ctx.message.author.remove_roles(role)
            await ctx.send("Role removed.")       
    else:
        await ctx.send("That role doesn't exist, or you don't have permission to modify it.")

@bot.command()
async def activities(ctx):
    """Lists the activities that this bot can simulate."""
    embed = discord.Embed(description="Activities", title="List of activies available for simulation")
    for importer, modname, ispkg in pkgutil.iter_modules(dropsims.__path__):
        module = importlib.import_module("dropsims." + modname)
        embed.add_field(name=modname, value=module.description)
    await ctx.send(embed=embed)

@bot.command()
async def dry(ctx, name: str, trials = 100, extraArg1 = "True", extraArg2 = "False"):
    """Calculates the probability of a dry streak at an activity.
    Syntax:
        !dry activity ?*ignoretrash
    parameters:
        activity - The activity to simulate (bandos, corp,.. See !activities)
        ignoretrash - Whether to exclude the drops generally considered trash (jars, etc)
    
    Note: ? denotes optional. * denotes boolean (True or False, case sensitive))"""
    if name == "tob":
        if extraArg1 == "True":
            extraArg1 = "4"
        probability = tob.dry(trials, int(extraArg1), extraArg2 == "True")
        title = "Chance of going " + str(trials) + " dry at the Theatre of Blood, with a team size of " + \
            extraArg1 + ""
        if extraArg2 == "False":
            title += ", where you do not get MvP in any room:\n\n"
        else: 
            title += ", where you get MvP in every room:\n\n" 
        title += str(probability * 100) + "%\n"
    else:
        probability, trashDrops = dropsims.dry(name, trials, extraArg1 == True)
        title = "Chance of going " + str(trials) + " dry at " + name + ": " + str(probability * 100) + "%\n"
    description = probabilityFlavourText.getFlavour(probability)
    embed = discord.Embed(title=title, description=description)
    if extraArg1 == "True" and name != "tob":
        embed.set_footer(text="Ignored drops: " + str(trashDrops))
    await ctx.send(embed=embed)

@dry.error
async def dry_error(ctx, error):
    await ctx.send("Invalid !dry arguments.\nSyntax: !dry name trials\n" + str(error))
    print(error)

if __name__ == '__main__':
    print("BOT1412 Beginning")
    bot.run(DISCORD_TOKEN)