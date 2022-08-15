urls = ["http://104.16."+str(i)+".86/cdn-cgi/traces" for i in range(0,10)]
import aiohttp
import asyncio
import requests
 
async def get_request(url):
    async with aiohttp.ClientSession() as cs:
        async with await cs.get(url) as response:
            return await response.text()
 
def parse(task):
    print(task.result().split("\n")[6])
 
tasks = []
for url in urls:
    c = get_request(url)
    task = asyncio.ensure_future(c)
    task.add_done_callback(parse)
    tasks.append(task)
 
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
