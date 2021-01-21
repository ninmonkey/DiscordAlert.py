from os import error
import re
import discord_webhook
import requests
import typing
from discord_webhook import DiscordWebhook
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import (
    Text,
    TypedDict,
    TypeVar,
    ByteString,
    List,
    MutableSet,
    MutableMapping,
    MutableSequence,
    Hashable,
    Dict,
    DefaultDict,
    OrderedDict,
    Any,
    AnyStr,
)
from pprint import pprint


appRoot: Path = Path(".")
configPath: Path = appRoot / "data/post_history.json"
# global session
config: Dict[str, Any] = {"WebhookUrl": None, "SkipPosting": True}


def initApp() -> None:
    """config loads user's webhook url[s]"""
    global config

    appConfig: Path = appRoot / ".private/config.json"
    configJsontoken = json.loads(appConfig.read_text("utf8", errors="strict"))
    config["WebhookUrl"] = configJsontoken["WebhookUrl"]
    # print(config["WebhookUrl"])


def find_powerbi_post(source_url: Text) -> List[Dict]:
    """Find power bi news. currently finds
    - 'feature summary' posts

    :param source_url: Url to scrape, ex: "https://powerbi.microsoft.com/en-us/blog/category/announcements"
    """
    re_summary = re.compile(".*feature.*summary.*", re.IGNORECASE)
    r = requests.get(source_url)
    soup = BeautifulSoup(r.text, "html.parser")

    all_urls = soup.select("a")
    some_urls = [elem for elem in all_urls if re_summary.match(elem.text) is not None]
    manual_urls: List[Dict] = []

    for elem in all_urls:
        maybeMatch = re_summary.search(elem.text)
        if maybeMatch is not None:
            meta = {
                "href": "https://powerbi.microsoft.com" + elem["href"],
                "title": elem["title"],
                "text": elem.text,
            }
            manual_urls.append(meta)

    return manual_urls
    if False:

        def has_class_but_no_id(tag):
            return tag.has_attr("class") and not tag.has_attr("id")

        results = soup.find_all(has_class_but_no_id)


def read_post_history() -> List[Dict]:
    """Returns 'post_history' as Json"""
    rawText: Text = configPath.read_text("utf8")
    data = json.loads(rawText)
    return data


def write_post_history() -> None:
    """writes 'post_history' as Json
    - save webhook id with post url, to allow multiple webhook urls"""
    pass


def is_already_posted(url: Text) -> bool:
    """Was post already logged in 'post_history.json' ?"""
    r: List[Dict] = read_post_history()
    is_posted: bool = any([line for line in r if line["url"] == url])
    return is_posted


def main() -> None:
    print("Post history:")
    pprint(read_post_history())

    "writing history"
    return
    if True:  # case: find PBI summaries
        source_url: Text = (
            "https://powerbi.microsoft.com/en-us/blog/category/announcements/"
        )
        foundSummaries: List[Any] = find_powerbi_post(source_url)

        pprint(foundSummaries)

    print("Check self log whether update was sent already")

    if not config["SkipPosting"]:
        for found in foundSummaries:
            webhook = DiscordWebhook(url=config["WebhookUrl"], content=found["href"])
            response = webhook.execute()
            print(f"fired {response}")


if __name__ == "__main__":
    initApp()
    main()