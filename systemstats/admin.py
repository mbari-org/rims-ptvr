from django.contrib import admin
from systemstats.models import MinuteStats

class MinuteStatsAdmin(admin.ModelAdmin):
    readonly_fields = (
            'timestamp',
            'camera_name',
            'temperature',
            'humidity',
            'pressure',
            'counts',
            'elapsed_time',
            'log_string',

    )

    fieldsets = [
            ('Basic Stats', {
                'fields': [
                    'timestamp',
                    'camera_name',
                    'temperature',
                    'humidity',
                    'pressure',
                    'counts',
                    'elapsed_time',
                    'log_string'
                ]
            })
    ]

    list_display = (
            'timestamp',
            'camera_name',
            'temperature',
            'humidity',
            'counts',
            'elapsed_time',
    )

    list_filter = ['timestamp']

# Register your models here.
admin.site.register(MinuteStats,MinuteStatsAdmin)
