from django.shortcuts import render, redirect, get_object_or_404
from .models import ChastityBeltType
from .forms import ChastityBeltTypeForm
from django.db.models import Sum
from datetime import timedelta

def belt_list(request):
    belts = ChastityBeltType.objects.all()

    # Aktuell getragener Gürtel
    currently_worn = WearingTime.objects.filter(endtime__isnull=True).first()
    currently_worn_belt_id = currently_worn.chastitybelttype.id if currently_worn and currently_worn.chastitybelttype else None
    currently_worn_start_time = currently_worn.starttime if currently_worn else None
    currently_worn_id = currently_worn.id if currently_worn else None

    # Dauer der aktuellen Tragezeit
    currently_worn_duration = ""
    if currently_worn:
        duration = timezone.now() - currently_worn.starttime
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        currently_worn_duration = f"{days} Tage, {hours} Std., {minutes} Min."

    # Gesamttragezeit pro Gürtel berechnen
    belt_total_wearing_times = {}
    for belt in belts:
        # Alle beendeten Tragezeiten für diesen Gürtel
        wearing_times = WearingTime.objects.filter(
            chastitybelttype=belt,
            endtime__isnull=False
        )
        # Summe der Dauer aller Tragezeiten
        total_duration = timedelta()
        for wt in wearing_times:
            total_duration += wt.endtime - wt.starttime
        # In Tage, Stunden, Minuten umrechnen
        days = total_duration.days
        hours, remainder = divmod(total_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        belt_total_wearing_times[belt.id] = f"{days} Tage, {hours} Std., {minutes} Min."

    return render(request, 'BeltTracker/belt_list.html', {
        'belts': belts,
        'currently_worn_belt_id': currently_worn_belt_id,
        'currently_worn_start_time': currently_worn_start_time,
        'currently_worn_duration': currently_worn_duration,
        'currently_worn_id': currently_worn_id,
        'belt_total_wearing_times': belt_total_wearing_times,  # Gesamttragezeit pro Gürtel
    })

def add_belt(request):
    if request.method == 'POST':
        form = ChastityBeltTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('belt_list')
    else:
        form = ChastityBeltTypeForm()
    return render(request, 'BeltTracker/add_belt.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import ChastityBeltType
from .forms import ChastityBeltTypeForm

def delete_belt(request, belt_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Nur POST-Anfragen sind erlaubt.")

    belt = get_object_or_404(ChastityBeltType, id=belt_id)
    belt.delete()
    return redirect('belt_list')

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import ChastityBeltType, WearingTime

# --- Tragezeiten ---
def wearing_time_list(request):
    wearing_times = WearingTime.objects.all().order_by('-starttime')
    belts = ChastityBeltType.objects.all()

    # Dauer für jede Tragezeit vorab berechnen
    for wt in wearing_times:
        if wt.endtime:
            duration = wt.endtime - wt.starttime
            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            wt.duration_str = f"{days} Tage, {hours} Std., {minutes} Min."
        else:
            wt.duration_str = "Läuft noch"

    return render(request, 'BeltTracker/wearing_time_list.html', {
        'wearing_times': wearing_times,
        'belts': belts
    })

def start_wearing_time(request):
    if request.method == 'POST':
        belt_id = request.POST.get('chastitybelttype')
    else:
        belt_id = request.GET.get('belt_id')  # Für den "Anlegen"-Link im Dropdown

    if belt_id:
        belt = get_object_or_404(ChastityBeltType, id=belt_id)
        # Beende eventuell laufende Tragezeit
        WearingTime.objects.filter(endtime__isnull=True).update(endtime=timezone.now())
        # Starte neue Tragezeit
        WearingTime.objects.create(
            chastitybelttype=belt,
            starttime=timezone.now()
        )
    return redirect('belt_list')

def end_wearing_time(request, wearing_time_id):
    wearing_time = get_object_or_404(WearingTime, id=wearing_time_id, endtime__isnull=True)
    wearing_time.endtime = timezone.now()
    wearing_time.save()
    return redirect('wearing_time_list')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

@csrf_exempt  # Nur für Tests! Im Produktivmodus CSRF-Token verwenden.
def update_wearing_time(request, wearing_time_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Nur POST-Anfragen sind erlaubt.'})

    wt = get_object_or_404(WearingTime, id=wearing_time_id)
    field = request.POST.get('field')
    value = request.POST.get('value')

    try:
        new_time = parse_datetime(value)
        if not new_time:
            return JsonResponse({'success': False, 'error': 'Ungültiges Datumsformat.'})

        if field == 'starttime':
            wt.starttime = new_time
        elif field == 'endtime':
            wt.endtime = new_time
        else:
            return JsonResponse({'success': False, 'error': 'Ungültiges Feld.'})

        wt.save()

        # Berechne die neue Dauer (falls Endzeit gesetzt ist)
        new_duration = ""
        if wt.endtime:
            duration = wt.endtime - wt.starttime
            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            new_duration = f"{days} Tage, {hours} Std., {minutes} Min."

        return JsonResponse({
            'success': True,
            'new_duration': new_duration
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})