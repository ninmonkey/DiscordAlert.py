# from os import error, sep, truncate
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
config: Dict[str, Any] = {"WebhookUrl": None, "SkipPosting": False}


def initApp() -> None:
    """config loads user's webhook url[s]"""
    global config

    appConfig: Path = appRoot / ".private/config.json"
    configJsontoken = json.loads(appConfig.read_text("utf8", errors="strict"))
    config["WebhookUrl"] = configJsontoken["WebhookUrl"]


def find_powerbi_post(source_url: Text) -> List[Dict]:
    """Find power bi news. currently finds
    - 'feature summary' posts

    :param source_url: Url to scrape, ex: "https://powerbi.microsoft.com/en-us/blog/category/announcements"
    """
    re_summary = re.compile(".*feature.*summary.*", re.IGNORECASE)
    r = requests.get(source_url)
    soup = BeautifulSoup(r.text, "html.parser")

    all_urls = soup.select("a")
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


def read_post_history() -> List[Dict]:
    """Returns 'post_history' as Json"""
    rawText: Text
    try:
        rawText = configPath.read_text("utf8")
    except FileNotFoundError:
        rawText = "[]"

    data = json.loads(rawText)
    return data


def append_post_history(postings: List[Dict]) -> None:
    """writes 'post_history' as Json
    - saves webhook id with post url, to allow multiple webhook urls

    :param postings: list of dicts containing keys: {'href'}
    """
    history: List[Any] = read_post_history()
    for post in postings:
        if is_already_posted(post["href"]):
            continue
        meta = {"url": post["href"], "webhook": config["WebhookUrl"]}
        history.append(meta)

    jsonText = json.dumps(history, indent=0, sort_keys=True)
    configPath.write_text(jsonText, "utf8")
    print("Wrote history log.")


def is_already_posted(url: Text) -> bool:
    """Was post already logged in 'post_history.json' ?
    :param url: full url to test
    """
    r: List[Dict] = read_post_history()
    is_posted: bool = any([line for line in r if line["url"] == url])
    return is_posted


def main() -> None:
    foundSummaries: List[Dict] = []
    print("Post history:")
    pprint(read_post_history())

    source_url: Text = (
        "https://powerbi.microsoft.com/en-us/blog/category/announcements/"
    )
    foundSummaries = find_powerbi_post(source_url)
    print("FoundSummaries:", foundSummaries)

    newPostings = [
        post for post in foundSummaries if not is_already_posted(post["href"])
    ]
    print("NewSummaries:", newPostings)

    if not config["SkipPosting"]:
        for found in newPostings:
            webhook = DiscordWebhook(url=config["WebhookUrl"], content=found["href"])
            response = webhook.execute()
            print(f"fired {response}")
        append_post_history(newPostings)
    else:
        print("SkipPosting = True")


if __name__ == "__main__":
    initApp()
    main()