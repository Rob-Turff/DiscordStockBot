import asyncio
import datetime
import discord
import logging
import urllib.request
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO)

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!sb'):
        commands = str(message.content).split(' ')
        if len(commands) == 1 or commands[1] == 'help':
            await message.channel.send(
                '!sb [shop shorthand] [item url] [size] [search interval (mins)] (optional) \nUse !sb list for '
                'available shops!')
        if commands[1] == "list":
            await print_available_shops(message)
        if len(commands) >= 4:
            await handle_shop_commands(message, commands)


async def handle_shop_commands(message, commands):
    current_time = datetime.datetime.now()
    search_length = 14
    added_time = datetime.timedelta(days=search_length)
    cutoff_time = current_time + added_time
    logging.info("Started search for size " + commands[3] + " at: " + commands[2])

    if len(commands) == 5:
        sleep_length = commands[4] * 60
    else:
        sleep_length = 900

    if commands[1] == 'jl':
        await handle_jl_command(message, commands, current_time, cutoff_time, sleep_length)
    if commands[1] == 'ff':
        await handle_ff_command(message, commands, current_time, cutoff_time, sleep_length)
    else:
        await message.channel.send("Store not recognised")
        await print_available_shops(message)

async def print_available_shops(message):
    available_shops = {"John Lewis": "jl", "FatFace": "ff"}
    string = ""
    for val in available_shops:
        string += "\n" + val + ": " + available_shops.get(val)
    await message.channel.send("Here is a list of supported shops: " + string)


async def get_website_html(url):
    page = urllib.request.urlopen(url)
    bytes = page.read()
    page_decoded = bytes.decode("utf8")
    parsed_html = BeautifulSoup(page_decoded)
    page.close()
    return parsed_html


async def handle_jl_command(message, commands, current_time, cutoff_time, sleep_length):
    while current_time < cutoff_time:
        parsed_html = await get_website_html(commands[2])
        sizes = parsed_html.body.findAll("li", {"class": "item--EzEuW"})
        for size in sizes:
            if size.text == commands[3]:
                if not re.search("class=\"disabled", str(size)):
                    await message.author.send("Product available in size " + commands[3] + " at: " + commands[2])
                    return
        await asyncio.sleep(sleep_length)
    await message.author.send("Product search expired for size " + commands[3] + " at: " + commands[2])


async def handle_ff_command(message, commands, current_time, cutoff_time, sleep_length):
    while current_time < cutoff_time:
        parsed_html = await get_website_html(commands[2])
        sizes = parsed_html.body.findAll("a", {"class": "b-variation__link swatchanchor selectable size"})
        for size in sizes:
            if size.text.strip() == commands[3]:
                await message.author.send("Product available in size " + commands[3] + " at: " + commands[2])
                return
        await asyncio.sleep(sleep_length)
    await message.author.send("Product search expired for size " + commands[3] + " at: " + commands[2])


client.run('NzE1OTUzNjA2NTY1ODIyNTE1.XvExJQ.F_R1MfqhMRXIpj_uU_W4Gd667gw')
