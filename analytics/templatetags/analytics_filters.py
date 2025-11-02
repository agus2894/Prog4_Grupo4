from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica dos valores"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Resta dos valores"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_days(value, days):
    """Suma días a una fecha"""
    try:
        from datetime import timedelta
        return value + timedelta(days=int(days))
    except (ValueError, TypeError):
        return value

@register.filter
def truncatechars(value, max_length):
    """Trunca un string a una longitud máxima"""
    if len(str(value)) > max_length:
        return str(value)[:max_length-3] + "..."
    return str(value)