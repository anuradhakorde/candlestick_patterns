from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """
    Get value from dictionary by key
    Usage: {{ mydict|dict_get:"mykey" }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def get_item(dictionary, key):
    """
    Alternative filter for getting dictionary items
    Usage: {{ mydict|get_item:"mykey" }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''