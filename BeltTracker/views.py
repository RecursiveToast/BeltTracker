from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, Count, Q
from .models import ChastityBeltType, WearingTime, Event
from .forms import ChastityBeltTypeForm
import json
from datetime import timedelta

# --- Gürtel ---
def belt_list(request):
    belts = ChastityBeltType.objects.all()

    # Aktuell getragener Gürtel
    currently_worn = WearingTime.objects.filter(endtime__isnull=True).first()
    currently_worn_belt_id = currently_worn.chastitybelttype.id if currently_worn and currently_worn.chastitybelttype else None
    currently_worn_start_time = currently_worn.starttime if currently_worn else None
    currently_worn_id = currently_worn.id if currently_worn else None

    # Gesamttragezeit pro Gürtel berechnen
    belt_total_wearing_times = {}
    for belt in belts:
        wearing_times = WearingTime.objects.filter(chastitybelttype=belt)
        total_duration = timedelta()
        for wt in wearing_times:
            end_time = wt.endtime if wt.endtime else timezone.now()
            total_duration += end_time - wt.starttime
        belt_total_wearing_times[belt.id] = total_duration

    return render(request, 'BeltTracker/belt_list.html', {
        'belts': belts,
        'currently_worn_belt_id': currently_worn_belt_id,
        'currently_worn_start_time': currently_worn_start_time,
        'currently_worn_id': currently_worn_id,
        'belt_total_wearing_times': belt_total_wearing_times,
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

def delete_belt(request, belt_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Nur POST-Anfragen sind erlaubt.")
    belt = get_object_or_404(ChastityBeltType, id=belt_id)
    belt.delete()
    return redirect('belt_list')

# --- Tragezeiten ---
def wearing_time_list(request):
    wearing_times = WearingTime.objects.all().order_by('-starttime')
    belts = ChastityBeltType.objects.all()

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
        belt_id = request.GET.get('belt_id')

    if belt_id:
        belt = get_object_or_404(ChastityBeltType, id=belt_id)
        WearingTime.objects.filter(endtime__isnull=True).update(endtime=timezone.now())
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

@csrf_exempt
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

# --- Events ---
@csrf_exempt
def add_event(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Nur POST-Anfragen sind erlaubt.'})

    try:
        data = json.loads(request.body)
        event_type = data.get('type')
        event_date_str = data.get('date')
        description = data.get('description', '')
        belt_id = data.get('belt_id')  # NEU: Gürtel-ID für Zuordnung

        event_date = timezone.datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))

        # Event erstellen
        event = Event.objects.create(
            type=event_type,
            date=event_date,
            description=description,
            belt_id=belt_id if belt_id else None
        )

        return JsonResponse({'success': True, 'event_id': event.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# NEU: Event bearbeiten (statt neu erstellen)
@csrf_exempt
def edit_event(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Nur POST-Anfragen sind erlaubt.'})

    try:
        event = get_object_or_404(Event, id=event_id)
        data = json.loads(request.body)

        event.type = data.get('type', event.type)
        event.date = timezone.datetime.fromisoformat(data.get('date', event.date.isoformat()).replace('Z', '+00:00'))
        event.description = data.get('description', event.description)
        event.belt_id = data.get('belt_id', event.belt_id if event.belt else None)
        event.save()

        return JsonResponse({'success': True, 'event_id': event.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# NEU: Dashboard-View
def dashboard(request):
    # Aktueller Gürtel
    currently_worn = WearingTime.objects.filter(endtime__isnull=True).first()
    current_belt = currently_worn.chastitybelttype if currently_worn else None

    # Aktuelle Tragezeit (Echtzeit)
    current_duration = None
    if currently_worn:
        current_duration = timezone.now() - currently_worn.starttime

    # Lieblingsgürtel (am meisten getragen)
    belt_usage = {}
    all_wearing_times = WearingTime.objects.filter(endtime__isnull=False)
    for wt in all_wearing_times:
        if wt.chastitybelttype:
            belt_id = wt.chastitybelttype.id
            duration = wt.endtime - wt.starttime
            belt_usage[belt_id] = belt_usage.get(belt_id, timedelta()) + duration

    favorite_belt = None
    if belt_usage:
        favorite_belt_id = max(belt_usage.items(), key=lambda x: x[1].total_seconds())[0]
        favorite_belt = ChastityBeltType.objects.get(id=favorite_belt_id)
        favorite_belt_duration = belt_usage[favorite_belt_id]

    # Letzte Reinigung des aktuellen Gürtels
    last_cleaning = None
    if current_belt:
        last_cleaning_event = Event.objects.filter(
            belt=current_belt,
            type__in=['cleaning', 'basiccleaning']
        ).order_by('-date').first()
        last_cleaning = last_cleaning_event.date if last_cleaning_event else None

    # Daten für Kreisdiagramm: Anteil der Tragezeiten seit erstem Eintrag
    first_entry = WearingTime.objects.order_by('starttime').first()
    if first_entry:
        all_times_since_first = WearingTime.objects.filter(starttime__gte=first_entry.starttime)
        total_time = timedelta()
        belt_times = {}
        no_belt_time = timedelta()

        for wt in all_times_since_first:
            end_time = wt.endtime if wt.endtime else timezone.now()
            duration = end_time - wt.starttime
            total_time += duration

            if wt.chastitybelttype:
                belt_id = wt.chastitybelttype.id
                belt_times[belt_id] = belt_times.get(belt_id, timedelta()) + duration
            else:
                no_belt_time += duration

        # Daten für Chart.js
        chart_labels = []
        chart_data = []
        chart_colors = []

        for belt_id, duration in belt_times.items():
            belt = ChastityBeltType.objects.get(id=belt_id)
            chart_labels.append(belt.name)
            chart_data.append(duration.total_seconds())
            chart_colors.append(f"#{hash(belt.name) & 0xFFFFFF:06x}")  # Zufarben basierend auf Namen

        if no_belt_time.total_seconds() > 0:
            chart_labels.append("Ohne Gürtel")
            chart_data.append(no_belt_time.total_seconds())
            chart_colors.append("#9E9E9E")

        chart_data_json = json.dumps(chart_data)
        chart_labels_json = json.dumps(chart_labels)
        chart_colors_json = json.dumps(chart_colors)
    else:
        chart_labels_json = json.dumps([])
        chart_data_json = json.dumps([])
        chart_colors_json = json.dumps([])

    return render(request, 'BeltTracker/dashboard.html', {
        'current_belt': current_belt,
        'current_duration': current_duration,
        'favorite_belt': favorite_belt,
        'favorite_belt_duration': favorite_belt_duration if favorite_belt else None,
        'last_cleaning': last_cleaning,
        'chart_labels': chart_labels_json,
        'chart_data': chart_data_json,
        'chart_colors': chart_colors_json,
    })