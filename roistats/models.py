from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class DailyHistograms(models.Model):
    day = models.DateField('Date',editable=False,db_index=True)
    camera = models.ForeignKey('rois.Camera',null=True)
    total_rois = models.PositiveIntegerField('Total ROIs',
            editable=False,db_index=True,default=0)

    length_bins = ArrayField(models.FloatField(),null=True)
    length_counts = ArrayField(models.PositiveIntegerField(),null=True)
    aspect_bins = ArrayField(models.FloatField(),null=True)
    aspect_counts = ArrayField(models.PositiveIntegerField(),null=True)
    class Meta:
        ordering = ('day',)

    def camera_name(self):
        return self.camera.name

class DailyStats(models.Model):

    day = models.DateField('Date',editable=False,db_index=True)
    camera = models.ForeignKey('rois.Camera',null=True)
    total_rois = models.PositiveIntegerField('Total ROIs',
            editable=False,db_index=True,default=0)
    average_major_length = models.PositiveSmallIntegerField(
            'Average Major Axis Length',editable=False,
            db_index=True,default=0)
    average_minor_length = models.PositiveSmallIntegerField(
            'Average Minor Axis Length',editable=False,
            db_index=True,default=0)
    median_major_length = models.PositiveSmallIntegerField(
            'Median Major Axis Length',editable=False,
            db_index=True,default=0)
    median_minor_length = models.PositiveSmallIntegerField(
            'Median Minor Axis Length',editable=False,
            db_index=True,default=0)
    stddev_major_length = models.PositiveSmallIntegerField(
            'Median Major Axis Length',editable=False,
            db_index=True,default=0)
    stddev_minor_length = models.PositiveSmallIntegerField(
            'Median Minor Axis Length',editable=False,
            db_index=True,default=0)
    class Meta:
        ordering = ('day',)

    def camera_name(self):
        return self.camera.name

class HourlyStats(models.Model):

    hour = models.DateTimeField('Hour',editable=False,db_index=True)
    camera = models.ForeignKey('rois.Camera',null=True)
    total_rois = models.PositiveIntegerField('Total ROIs',
            editable=False,db_index=True,default=0)
    average_major_length = models.PositiveSmallIntegerField(
            'Average Major Axis Length',editable=False,
            db_index=True,default=0)
    average_minor_length = models.PositiveSmallIntegerField(
            'Average Minor Axis Length',editable=False,
            db_index=True,default=0)
    median_major_length = models.PositiveSmallIntegerField(
            'Median Major Axis Length',editable=False,
            db_index=True,default=0)
    median_minor_length = models.PositiveSmallIntegerField(
            'Median Minor Axis Length',editable=False,
            db_index=True,default=0)
    stddev_major_length = models.PositiveSmallIntegerField(
            'Median Major Axis Length',editable=False,
            db_index=True,default=0)
    stddev_minor_length = models.PositiveSmallIntegerField(
            'Median Minor Axis Length',editable=False,
            db_index=True,default=0)
    class Meta:
        ordering = ('hour',)

    def camera_name(self):
        return self.camera.name

