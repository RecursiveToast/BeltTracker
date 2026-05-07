from .models import WearingTime, ChastityBeltType
from django.utils import timezone

def currently_worn_belt(request):
    # Aktuell getragener Gürtel
    currently_worn = WearingTime.objects.filter(endtime__isnull=True).first()
    currently_worn_belt = currently_worn.chastitybelttype if currently_worn and currently_worn.chastitybelttype else None
    currently_worn_start_time = currently_worn.starttime if currently_worn else None

    return {
        'currently_worn_belt': currently_worn_belt,
        'currently_worn_start_time': currently_worn_start_time,
    }