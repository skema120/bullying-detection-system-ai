from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Custom filter to get an item from a dictionary by key."""
    return dictionary.get(key)


@register.filter
def ordinal(value):
    if value % 10 == 1 and value % 100 != 11:
        return f"{value}st"
    elif value % 10 == 2 and value % 100 != 12:
        return f"{value}nd"
    elif value % 10 == 3 and value % 100 != 13:
        return f"{value}rd"
    else:
        return f"{value}th"
