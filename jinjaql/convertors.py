# coding: utf-8
import re
import collections


ESCAPE_REGEX = re.compile(r"[\0\n\r\032\'\"\\]")
ESCAPE_MAP = {
    '\0': '\\0', '\n': '\\n', '\r': '\\r', '\032': '\\Z',
    '\'': '\\\'', '"': '\\"', '\\': '\\\\'
}


class SnaqlGuardException(Exception):
    pass


def escape_string(value):
    return ESCAPE_REGEX.sub(lambda match: ESCAPE_MAP.get(match.group(0)), value)


def guard_string(value):
    if not value:
        return "''"

    return "'%s'" % escape_string(value)


def guard_bool(value):
    return 1 if value else 0


def guard_integer(value):
    if not value:
        return value
    try:
        return int(value)
    except (TypeError, ValueError) as e:
        raise SnaqlGuardException(e.args[0])


def guard_datetime(obj):
    if not obj:
        return obj

    try:
        if obj.microsecond:
            fmt = (
                "'{0.year:04}-{0.month:02}-{0.day:02} "
                "{0.hour:02}:{0.minute:02}:{0.second:02}.{0.microsecond:06}'"
            )
        else:
            fmt = (
                "'{0.year:04}-{0.month:02}-{0.day:02} "
                "{0.hour:02}:{0.minute:02}:{0.second:02}'"
            )
        return fmt.format(obj)
    except (AttributeError, ValueError) as e:
        raise SnaqlGuardException(e.args[0])


def guard_date(obj):
    if not obj:
        return obj

    fmt = "'{0.year:04}-{0.month:02}-{0.day:02}'"

    try:
        return fmt.format(obj)
    except (AttributeError, ValueError) as e:
        raise SnaqlGuardException(e.args[0])


def guard_float(value):
    if not value:
        return value

    try:
        value = float(value)
        return "%.15g" % value
    except (TypeError, ValueError) as e:
        raise SnaqlGuardException(e.args[0])


def guard_timedelta(obj):
    if not obj:
        return obj

    try:
        seconds = int(obj.seconds) % 60
        minutes = int(obj.seconds // 60) % 60
        hours = int(obj.seconds // 3600) % 24 + int(obj.days) * 24
        if obj.microseconds:
            fmt = "'{0:02d}:{1:02d}:{2:02d}.{3:06d}'"
        else:
            fmt = "'{0:02d}:{1:02d}:{2:02d}'"

        return fmt.format(hours, minutes, seconds, obj.microseconds)
    except (AttributeError, ValueError) as e:
        raise SnaqlGuardException(e.args[0])


def guard_time(obj):
    if not obj:
        return obj

    try:
        if obj.microsecond:
            fmt = "'{0.hour:02}:{0.minute:02}:{0.second:02}.{0.microsecond:06}'"
        else:
            fmt = "'{0.hour:02}:{0.minute:02}:{0.second:02}'"

        return fmt.format(obj)
    except (AttributeError, ValueError) as e:
        raise SnaqlGuardException(e.args[0])


def guard_case(value, items=None):
    if not value:
        return value

    items = items or set()
    if not isinstance(items, collections.abc.Iterable):
        raise SnaqlGuardException('Guard items are not iterable')

    items = set(items)
    if value not in items:
        raise SnaqlGuardException(
            '%s expected, "%s" is bad value' % (', '.join(items), value)
        )
    return value


def guard_regexp(value, regexp):
    if not value:
        return value

    if re.match(regexp, value):
        return value
    else:
        raise SnaqlGuardException(
            '"%s" does not match "%s" expression' % (value, regexp)
        )
