import discord
from dotenv import load_dotenv
import asyncio
import aiohttp
import datetime
import os
import webserver

load_dotenv() 

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))  # Ensure this is an integer
API_URL = 'https://haitou.zhitongguigu.com/api/search'
POST_PAYLOAD = {"direction":"sde,quant","duration":"","exp":"intern","tag":"","inFavorite":"","methodName":"changeDirection","education":"","remote":"","sponsor":"","country":"","pageIndex":0,"pageSize":30,"system":"US"}

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def call_api_and_send():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel ID {CHANNEL_ID} not found.")
        return

    while not client.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=POST_PAYLOAD) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        jobsList = data['data']['list']
                        filtered_jobs = [job for job in jobsList if job['createTime'] >= (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')]
                        
                        # TESTING VALUES
                        filtered_jobs = jobsList[:3]
                        
                        if filtered_jobs:
                            for job in filtered_jobs[::-1]:
                                embed = discord.Embed(
                                    title=job['title'],
                                    url=job['url'],
                                    description=f"Posted at: `{job['createTime']}`",
                                    color=discord.Color.blue()
                                )
                                embed.set_author(name=job['company'])
                                await channel.send(embed=embed)
                    else:
                        pass
                        await channel.send(f"API call failed with status code {response.status}")
        except Exception as e:
            await channel.send(f"Error during API call: {e}")
        
        await asyncio.sleep(600)  

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(call_api_and_send())

webserver.keep_alive()  # Start the web server to keep the bot alive
client.run(TOKEN)

