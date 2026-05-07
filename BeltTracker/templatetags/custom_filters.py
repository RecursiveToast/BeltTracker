from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def time_diff(end_time, start_time):
    if not end_time or not start_time:
        return ""
    duration = end_time - start_time
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} Tage, {hours} Std., {minutes} Min."

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")