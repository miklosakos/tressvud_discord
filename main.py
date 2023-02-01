from discord.ext import tasks
import discord, json, requests, os

VIDCHANNEL_ID = 343787813478727690
LIVECHANNEL_ID = 343787813478727690
TOKEN = 'bottoken'


class tressvud(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not os.path.exists("/tmp/vidid.txt"):
            tmpfile = open("/tmp/vidid.txt", 'w')
            tmpfile.write("dummy")
            tmpfile.close()

    async def setup_hook(self) -> None:
        self.fetch_tressvud.start()

    async def on_ready(self):
        print(f'Bejelentkeztem, mint {self.user}, azonosito: {self.user.id}')

    @tasks.loop(seconds=10)
    async def fetch_tressvud(self):

        tressvud_feed = None
        print("fetch_tressvud")
        try:
            tressvud_feed = requests.get("https://trashvod.com/api/v1/videos")
            print("tressvud_feed")
        except requests.exceptions.RequestException as e:
            print(str(e))
        with open('/tmp/vidid.txt','r') as tmpadat:
            tmpfile = tmpadat.readline()
        adat = json.loads(tressvud_feed.text)
        print("adat")
        if str(adat['data'][0]['uuid']) in tmpfile:
            print("no update")
        else:
            print("update")
            open("/tmp/vidid.txt", 'w').writelines(str(adat['data'][0]['uuid']))
            if adat['data'][0]['nsfw']:
                cim = f"18+ {adat['data'][0]['name']}"
                szin = discord.Color.dark_red()
            else:
                cim = adat['data'][0]['name']
                szin = discord.Color.dark_blue()
            video = discord.Embed(title=cim, url=adat['data'][0]['url'],
                                  description=adat['data'][0]['description'], color=szin)
            video.set_image(url=f"https://trashvod.com{adat['data'][0]['thumbnailPath']}")
            video.set_author(name=adat['data'][0]['account']['displayName'], url=adat['data'][0]['account']['url'])
            if adat['data'][0]['isLive']:
                channel = self.get_channel(LIVECHANNEL_ID)
            else:
                channel = self.get_channel(VIDCHANNEL_ID)
            await channel.send(embed=video)

    @fetch_tressvud.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = tressvud(intents=discord.Intents.default())
client.run(TOKEN)
