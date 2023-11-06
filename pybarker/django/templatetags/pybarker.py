import codecs
import re

from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe

from pybarker.utils.bbcoderender import render as bbcoderender
from pybarker.utils.string import truncate_smart

register = template.Library()


@register.simple_tag
def call_method(obj, methodname, *args, **kwargs):
    """
    Вызов метода объекта с параметрами.
    {% call_method project 'get_role_user_flag' role|role_from_fieldname as flag2 %}
    """
    method = getattr(obj, methodname, None)
    if method is None:
        return "no such method name %s" % methodname
    return method(*args, **kwargs)


@register.filter
def get_attribute(obj, name):
    """
    фильтр для получения значения атрибута объекта по его имени
    для динамического собирания имени метода, например
    {% if project|get_attribute:get_role_status_current = 'a' %}
    """
    return getattr(obj, name, "")


@register.filter
def get_item(dictionary, key):
    """
    фильтр для получения значения значения словаря по ключу
    для динамического собирания имени метода, например
    {{ form.is_stage_active_my|get_item:role }}
    используется именно взятие индекса, потому наличие __getitem__ достаточно, без всяких DictMixin итд
    если будет KeyError, то вернётся None
    """
    try:
        return dictionary[key]
    except KeyError:
        return None


@register.filter_function
def order_by(queryset, args):
    """
    {% for item in your_list|order_by:"field1,-field2,other_class__field_name"
    """
    args = [x.strip() for x in args.split(",")]
    return queryset.order_by(*args)


@register.filter
def get_range(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    https://djangosnippets.org/snippets/1357/
    """
    return list(range(value))


# аналог тега truncatechars, только точки вставляет не в конце а посередине
@register.filter(is_safe=True)
def truncatechars_smart(value, arg):
    try:
        length = int(arg)
    except ValueError:
        return value
    """
    strlen = len(value)
    if strlen < length:
        return value
    halflen = length // 2
    return value[0:halflen] + '...' + value[-halflen:]
    """
    return truncate_smart(value, length)


# вычитание, полный аналог стандартного add
@register.filter(is_safe=False)
def subtract(value, arg):
    """subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ""


# заменяет запятую на точку (для представления правильных дробных числе в странице, для js например)
# все нестроки превращает в строки
@register.filter
def replace_commadot(string):
    if string is None:
        return string
    string = force_str(string)
    return string.replace(",", ".")


@register.filter(is_safe=True)
def intspace(value):
    """
    Converts an integer to a string containing spaces every three digits.
    For example, 3000 becomes '3 000' and 45000 becomes '45 000'.
    """
    # http://softwaremaniacs.org/forum/django/19392/
    if value is None:
        return None
    orig = force_str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1> \g<2>", orig)
    return new if orig == new else intspace(new)


@register.filter
def bound_field(form, name):
    """
    returns bound field in form (напрямую по другому никак)
    {% with form|bound_field:role as field %}
    ...
    {% endwith %}
    """
    return form.__getitem__(name)


# подсвечивает активные ссылки на основании сравнения с указанным урлом
# http://stackoverflow.com/a/18772289/592813
# <li class="nav-home {% active 'url-name' %}"><a href="#">Home</a></li>
# <li class="nav-blog {% active '^/regex/' %}"><a href="#">Blog</a></li>
@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = "^" + reverse(pattern_or_urlname)
    except NoReverseMatch:
        # Reverse for 'urlname' not found. 'urlname' is not a valid view function or pattern name.
        # если недозадать параметры урла то будет:
        # Reverse for 'crm-projects' with no arguments not found. 1 pattern(s) tried: ['crm/projects/(?P<statuskey>[^/]+)/$']"
        # старый способ возможно более логичный: rm = resolve(request.path) -> rm.url_name
        pattern = pattern_or_urlname
    path = context["request"].path
    if re.search(pattern, path):
        return "active"
    return ""


# текущий урл в виде тега подходящего для class или id
# типа ncr:list -> ncr-list
# в виде {% currenturlnametag as as_menuid %} можно использовать как инфу о текущем местоположении проверяя по if... итд
@register.simple_tag(takes_context=True)
def currenturlnametag(context):
    resolver_match = context["request"].resolver_match
    if resolver_match is None:  # при 404 случается такое
        return "no-page"
    return "%s-%s" % ("-".join(resolver_match.namespaces), resolver_match.url_name)


# простая конкатенация строк, add работает криво если одно число целое
@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.filter(is_safe=True)
def bbcode(value):
    return mark_safe(bbcoderender(value))


# фильтр, возвращает true/false согласно возврату метода startswith на строке
@register.filter("startswith")
def startswith_filter(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


# фильтр, метод split на строке
@register.filter(name="split")
def slpit_filter(value, arg, autoescape=True):
    arg = codecs.decode(arg, "unicode-escape")  # unescape \n etc
    return value.split(arg)
