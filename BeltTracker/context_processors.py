from .models import WearingTime, ChastityBeltType, Event
from django.utils import timezone
from datetime import timedelta

def currently_worn_belt(request):
    currently_worn = WearingTime.objects.filter(endtime__isnull=True).first()
    currently_worn_belt = currently_worn.chastitybelttype if currently_worn and currently_worn.chastitybelttype else None
    currently_worn_start_time = currently_worn.starttime if currently_worn else None
    currently_worn_id = currently_worn.id if currently_worn else None

    return {
        'currently_worn_belt': currently_worn_belt,
        'currently_worn_start_time': currently_worn_start_time,
        'currently_worn_id': currently_worn_id,  # NEU: ID für Bauchbinde
    }

# Zentraler Kontext-Prozessor für Tragezeit (Single Source of Truth)
def current_wearing_time(request):
    currently_worn = WearingTime.objects.filter(endtime__isnull=True).first()

    if currently_worn:
        duration = timezone.now() - currently_worn.starttime
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        seconds = duration.seconds % 60
        duration_str = f"{days} Tage, {hours} Std., {minutes} Min., {seconds} Sek."
        return {
            'current_wearing_time': duration_str,
            'current_wearing_time_seconds': duration.total_seconds(),
            'current_wearing_time_obj': currently_worn,
        }
    else:
        return {
            'current_wearing_time': None,
            'current_wearing_time_seconds': 0,
            'current_wearing_time_obj': None,
        }