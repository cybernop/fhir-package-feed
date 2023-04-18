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


# Tue, 08 Nov 2022 10:35:08 +0100
GENERAL_PUB_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
# Tue, 08 Nov 2022 12:00:00 +0100 GMT
GENERAL_BUILD_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z %Z"
# Tue, Nov 8, 2022 22:28+0100+01:00
ITEM_BUILT_DATE_FORMAT = "%a, %b %d, %Y %H:%M%z"
# Tue, 08 Nov 2022 12:00:00 +0100 GMT
ITEM_PUB_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z %Z"

DATE_FORMATS = [
    GENERAL_BUILD_DATE_FORMAT,
    GENERAL_PUB_DATE_FORMAT,
    ITEM_BUILT_DATE_FORMAT,
    ITEM_PUB_DATE_FORMAT,
]


def __convert_to_datetime(value: str) -> datetime:
    error_expr = re.compile(r"unconverted data remains: (\S+)")
    for format in DATE_FORMATS:
        try:
            return datetime.strptime(value, format)
        except ValueError as e:
            if match := error_expr.match(str(e)):
                return datetime.strptime(value[: -len(match[1])], format)
            continue
    pass


def __convert_values_to_datetime(value: Dict, keys: List[str]) -> None:
    for key in keys:
        value[key] = __convert_to_datetime(value[key])


def load_data(file: str) -> Dict:
    data = json.loads(Path(file).read_text())

    __convert_values_to_datetime(data, ["pub_date", "last_build_date"])
    for data_item in data["items"]:
        __convert_values_to_datetime(data_item, ["built", "pub_date"])

    return data
