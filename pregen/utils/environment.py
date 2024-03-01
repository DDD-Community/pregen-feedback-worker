import os
from typing import Any

import tomli

from pregen.utils.singleton import singleton


@singleton
class Environments:
    config_path: str = os.getenv("CONFIG_PATH", "assets/config.toml")

    openai: [dict, Any] = dict()
    database: [dict, Any] = dict()
    message_queue: [dict, Any] = dict()
    file: [dict, Any] = dict()

    def __init__(self) -> None:
        with open(self.config_path, mode="rb") as fp:
            configs = tomli.load(fp)

        self.openai = configs["openai"]
        self.database = configs["database"]
        self.message_queue = configs["message_queue"]
        self.file = configs["file"]


_environments = Environments()


def get_envs() -> Environments:
    return _environments
