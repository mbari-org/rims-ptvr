from django.contrib import admin
from roistats.models import DailyStats, DailyHistograms

class DailyStatsAdmin(admin.ModelAdmin):
    readonly_fields = (
            'day',
            'camera',
            'total_rois',
            'average_major_length',
            'average_minor_length',

    )

    fieldsets = [
            ('Basic Stats', {
                'fields': [
                    'day',
                    'camera',
                    'total_rois',
                    'average_major_length',
                    'average_minor_length'
                ]
            })
    ]

    list_display = (
            'day',
            'camera_name',
            'total_rois'
    )

    list_filter = ['day']

class DailyHistogramsAdmin(admin.ModelAdmin):
    readonly_fields = (
            'day',
            'camera',
            'total_rois',
            'length_counts',
            'length_bins',
            'aspect_counts',
            'aspect_bins',

    )

    fieldsets = [
            ('Histograms', {
                'fields': [
                    'day',
                    'camera',
                    'total_rois',
                    'length_counts',
                    'aspect_counts'
                ]
            })
    ]

    list_display = (
            'day',
            'camera_name',
            'total_rois'
    )

    list_filter = ['day']

# Register your models here.
admin.site.register(DailyStats,DailyStatsAdmin)
admin.site.register(DailyHistograms,DailyHistogramsAdmin)
