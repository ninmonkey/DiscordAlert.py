from os import error
import typing
from discord_webhook import DiscordWebhook

import json
from pathlib import Path
from typing import (
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

appRoot: Path = Path(".")
# global session
config: Dict[str, Any] = {"WebhookUrl": None}


def initApp() -> None:
    global config

    appConfig: Path = appRoot / ".private/config.json"
    configJsontoken = json.loads(appConfig.read_text("utf8", errors="strict"))
    config["WebhookUrl"] = configJsontoken["WebhookUrl"]
    print(config["WebhookUrl"])


def main() -> Any:
    webhook = DiscordWebhook(url=config["WebhookUrl"], content="Webhook Message")
    response = webhook.execute()


if __name__ == "__main__":
    initApp()
    main()