from datetime import datetime
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S %z"


def _datetime_format(value: datetime):
    return value.strftime(DATETIME_FORMAT)


def render(data: Dict, output_file_path: str):
    output_file = Path(output_file_path)
    if not output_file.parent.exists():
        output_file.parent.mkdir(parents=True)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(),
        lstrip_blocks=True,
        trim_blocks=True,
    )
    env.filters["datetime_format"] = _datetime_format
    template = env.get_template("package-feed.xml")
    rendered = template.render(**data)

    output_file.write_text(rendered)
