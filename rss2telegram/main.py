import json
import logging as log
import os
import sys

import feedparser
import telebot
from bs4 import BeautifulSoup

from rss2telegram.models import Post, Settings
from rss2telegram.utils import convert_time_struct_to_dt

settings = Settings()
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
if settings.VERBOSE:
    log.basicConfig(format=LOG_FORMAT, level=log.DEBUG,
                    datefmt=LOG_DATE_FORMAT)
else:
    log.basicConfig(format=LOG_FORMAT, level=log.INFO, datefmt=LOG_DATE_FORMAT)


def main():
    log.info("Logging in to Telegram.")
    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
    new_posts: list[Post] = []
    if not os.path.exists(settings.POSTS_FILE):
        log.info("%s file does not exist, creating it", settings.POSTS_FILE)
        with open(settings.POSTS_FILE, "w", encoding="utf-8") as file_handler:
            json.dump([], file_handler)
        guids = []
    else:
        log.info("Using %s as posts file", settings.POSTS_FILE)
        with open(settings.POSTS_FILE, encoding="utf-8") as file_handler:
            guids = json.load(file_handler)

    log.info("Parsing feed from %s", settings.FEED)
    feed = feedparser.parse(settings.FEED)
    for entry in feed.entries:
        content = entry["description"]
        post = {}
        soup = BeautifulSoup(content, "html.parser")

        img_soup = soup.find("img")
        image = None
        if img_soup:
            image = img_soup["src"]
        text = "\n".join(soup.stripped_strings)
        text += f"\n\n{entry['link']}"

        post = Post(
            title=entry["title"],
            content=text,
            image=image,
            date=convert_time_struct_to_dt(entry["published_parsed"])
        )

        if entry["guid"] not in guids:
            log.info("Got new post %s", post.title)
            new_posts.append(post)
            guids.append(entry["guid"])

    if not new_posts:
        log.info("No new posts.")
        sys.exit(0)

    new_posts.sort(key=lambda x: x.date)
    for post in new_posts:
        log.info("Publishing post %s", post.title)
        content = f"**{post.title}**\n\n{post.content}"
        if post.image is not None:
            bot.send_photo(settings.CHANNEL_ID,
                           photo=post.image, caption=content)
        else:
            bot.send_message(settings.CHANNEL_ID, content)

    log.info("Updating %s posts file with new posts", settings.POSTS_FILE)
    with open(settings.POSTS_FILE, "w", encoding="utf-8") as file_handler:
        json.dump(guids, file_handler)


if __name__ == "__main__":
    main()
