from django.db import models

# Create your models here.

class MinuteStats(models.Model):

    timestamp = models.DateTimeField('Timestamp',null=True,editable=False,db_index=True)
    camera = models.ForeignKey('rois.Camera',null=True)
    temperature = models.FloatField('Temperature',null=True,editable=False)
    humidity = models.FloatField('Humidity',null=True,editable=False)
    pressure = models.FloatField('Pressure',null=True,editable=False)
    counts = models.PositiveIntegerField('Counts',null=True,editable=False)
    elapsed_time = models.PositiveIntegerField('Elapsed Time',null=True,editable=False)
    log_string = models.CharField(
            'LogString',max_length=1024,editable=False,null=True)
    camera_active = models.NullBooleanField(
            'Camera Active',editable=False,null=True)

    class Meta:
        ordering = ('timestamp',)

    def camera_name(self):
        return self.camera.name
