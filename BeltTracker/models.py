from django.db import models
from django.db.models import Sum

# Create your models here.
class ChastityBeltType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=256, blank=True)
    material = models.CharField(max_length=256)
    addons = models.ManyToManyField('ChastityBeltAddon', blank=True)

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"

class ChastityBeltAddon(models.Model):
    ADDON_CHOICES = [
        ('lock', 'Vorhängeschloss'),
        ('padlock', 'Zahlenschloss'),
        # Weitere Addons nach Bedarf
    ]

    type = models.CharField(
        max_length=20,
        choices=ADDON_CHOICES,
        unique=True  # Verhindert doppelte Addons in der Datenbank
    )

    def __str__(self):
        return self.get_type_display()  # Zeigt den lesbaren Namen an (z. B. "PA-Ring")

class WearingTime(models.Model):
    starttime = models.DateTimeField(auto_now_add=True)
    endtime = models.DateTimeField(null=True, blank=True)
    chastitybelttype = models.ForeignKey(
        ChastityBeltType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tragezeiten"
    )

    @property
    def get_duration_display(self):
        if not self.endtime:
            duration = timezone.now() - self.starttime
        else:
            duration = self.endtime - self.starttime

        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days} Tage, {hours} Std., {minutes} Min."

    def __str__(self):
        guertel_info = f" mit {self.chastitybelttype}" if self.chastitybelttype else ""
        return f"Tragezeit von {self.starttime} bis {self.endtime or 'jetzt'}{guertel_info}"

class Event(models.Model):
    eventtypes = [
        ('orgasm', 'Orgasmus'),
        ('injury', 'Verletzung'),
        ('cleaning', 'Reinigung'),
        ('basiccleaning', 'Grundreinigung'),
        ('adjustment', 'Einstellung')
    ]
    date = models.DateTimeField()
    description = models.TextField(blank=True)
    type = models.CharField(
        max_length=20,
        choices=eventtypes,
        default='cleaning'  # Standardwert
    )
    belt = models.ForeignKey(  # Zuordnung zu Gürtel (nicht zu WearingTime)
        'ChastityBeltType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    def __str__(self):
        return f"{self.get_type_display()} am {self.date.strftime('%Y-%m-%d %H:%M')}"
