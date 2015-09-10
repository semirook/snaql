# coding: utf-8
import re


ESCAPE_REGEX = re.compile(r"[\0\n\r\032\'\"\\]")
ESCAPE_MAP = {
    '\0': '\\0', '\n': '\\n', '\r': '\\r', '\032': '\\Z',
    '\'': '\\\'', '"': '\\"', '\\': '\\\\'
}


def escape_string(value):
    return (
        ESCAPE_REGEX.sub(
            lambda match: ESCAPE_MAP.get(match.group(0)), value)
    )
