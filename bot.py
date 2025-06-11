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
API_URL = os.getenv('API_URL')
POST_PAYLOAD = {"direction":"sde,quant","duration":"","exp":"intern","tag":"","inFavorite":"","methodName":"changeDirection","education":"","remote":"","sponsor":"","country":"","pageIndex":0,"pageSize":30,"system":"US"}

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def call_api_and_send():
        
    last_id = os.getenv('LAST_ID')

    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel ID {CHANNEL_ID} not found.")
        return

    # await channel.send("Connected!")
    
    while not client.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=POST_PAYLOAD) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobsList = data['data']['list']
                        
                        if last_id is not None:
                            filtered_jobs = []
                            found = False
                            for job in jobsList:
                                if job['id'] != last_id:
                                    filtered_jobs.append(job)
                                else:
                                    found = True
                                    break
                            if not found:
                                last_id = None
                                
                        if last_id is None:
                            filtered_jobs = [job for job in jobsList if job['createTime'] >= (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')]
        
                        last_id = filtered_jobs[0]['id'] if filtered_jobs else last_id
                        print(f"Last ID updated to: {last_id}")
                        
                        if filtered_jobs:
                            for job in filtered_jobs[::-1]:
                                embed = discord.Embed(
                                    title=job['title'],
                                    url=job['url'],
                                    timestamp=datetime.datetime.strptime(job['createTime'], '%Y-%m-%d %H:%M:%S'),
                                    color=discord.Color.blue()
                                )
                                embed.set_author(name=job['company'])
                                await channel.send(embed=embed)
                    else:
                        pass
                        await channel.send(f"API call failed with status code {response.status}")
                        
        except Exception as e:
            await channel.send(f"Error during API call: {e}")
            pass
        
        await asyncio.sleep(600)  

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(call_api_and_send())

webserver.keep_alive()  
client.run(TOKEN)

