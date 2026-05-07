from django.db import models

# Create your models here.
class ChastityBeltType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=256, blank=True)
    material = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"

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

class Maintenance(models.Model):
    maintenancetypes = [
        ('cleaning', 'Reinigung')
    ]
    date = models.DateTimeField()
    type = models.CharField(
        max_length=20,
        choices=maintenancetypes,
        default='cleaning'  # Standardwert
    )

    def __str__(self):
        return f"{self.type}"