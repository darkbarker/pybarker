import re


def render(value):
    bbdata = [
        (r'\[url\](.+?)\[/url\]', r'<a href="\1">\1</a>'),
        (r'\[url=(.+?)\](.+?)\[/url\]', r'<a href="\1">\2</a>'),
        (r'\[email\](.+?)\[/email\]', r'<a href="mailto:\1">\1</a>'),
        (r'\[email=(.+?)\](.+?)\[/email\]', r'<a href="mailto:\1">\2</a>'),
        (r'\[img\](.+?)\[/img\]', r'<img src="\1">'),
        (r'\[img=(.+?)\](.+?)\[/img\]', r'<img src="\1" alt="\2">'),
        (r'\[b\](.+?)\[/b\]', r'<b>\1</b>'),
        (r'\[i\](.+?)\[/i\]', r'<i>\1</i>'),
        (r'\[u\](.+?)\[/u\]', r'<u>\1</u>'),
        (r'\[s\](.+?)\[/s\]', r'<s>\1</s>'),
        (r'\[quote\](.+?)\[/quote\]', r'<blockquote>\1</blockquote>'),
        (r'\[center\](.+?)\[/center\]', r'<div align="center">\1</div>'),
        (r'\[code\](.+?)\[/code\]', r'<tt>\1</tt>'),
        (r'\[big\](.+?)\[/big\]', r'<big>\1</big>'),
        (r'\[small\](.+?)\[/small\]', r'<small>\1</small>'),
    ]

    for bbset in bbdata:
        p = re.compile(bbset[0], re.DOTALL)
        value = p.sub(bbset[1], value)

    # The following two code parts handle the more complex list statements
    temp = ''
    p = re.compile(r'\[list\](.+?)\[/list\]', re.DOTALL)
    m = p.search(value)
    if m:
        items = re.split(re.escape('[*]'), m.group(1))
        for i in items[1:]:
            temp = temp + '<li>' + i + '</li>'
        value = p.sub(r'<ul>' + temp + '</ul>', value)

    temp = ''
    p = re.compile(r'\[list=(.)\](.+?)\[/list\]', re.DOTALL)
    m = p.search(value)
    if m:
        items = re.split(re.escape('[*]'), m.group(2))
        for i in items[1:]:
            temp = temp + '<li>' + i + '</li>'
        value = p.sub(r'<ol type=\1>' + temp + '</ol>', value)

    value = value.replace('</blockquote>\n', '</blockquote>')
    value = value.replace('</div>\n', '</div>')

    # replace newline
    value = value.replace('\n', '<br />')

    return value


def bbcode_remove_tags(value):
    """Удаление тегов BBCode из строки."""

    pattern = r'\[[a-z]+=?.*?\].*?\[\/[a-z]+\]'
    return re.sub(pattern, '', value, flags=re.DOTALL)
