import datetime

import aiohttp
from discord.ext import commands, tasks
from html.parser import HTMLParser
import re


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    if bool(re.search("\d{4}/\d{2}/\d{2}", str(value))):
                        if value not in self.urls:
                            self.urls.append(value)


parser = MyHTMLParser()


class WebUpdates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coyotes_news_feed.start()

    @tasks.loop(seconds=600)
    async def coyotes_news_feed(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://gophnx.com/category/coyotes/") as response:
                html = await response.text()
                parser.feed(html)
                if parser.urls:
                    latest_article = str(parser.urls[0])
                    parser.urls = []
                else:
                    return

                if await self.bot.articles_database['news'].count_documents({"_id": "coyotes"}, limit=1) == 0:
                    coyotes_news_dict = {
                        "_id": "coyotes",
                        "latest_article": latest_article
                    }
                    await self.bot.articles_database['news'].insert_one(coyotes_news_dict)
                else:
                    coyotes_dict = await self.bot.articles_database['news'].find_one({"_id": "coyotes"})
                    if coyotes_dict['latest_article'] == latest_article:
                        return
                    else:
                        await self.bot.articles_database['news'].update_one({"_id": "coyotes"}, {"$set": {"latest_article": latest_article}})

                channel = self.bot.get_channel(888529400142901309)  # gets channel

                await channel.send(f"New Coyotes Post: \n {latest_article}")


def setup(bot):
    bot.add_cog(WebUpdates(bot))
