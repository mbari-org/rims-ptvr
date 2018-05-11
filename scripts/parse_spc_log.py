from rois.models import Image, PlanktonCamera
from systemstats.models import MinuteStats
import json
import datetime
import time
import smtplib
from email.mime.text import MIMEText
from subprocess import call
import pytz

base_dir = '/home/ptvradmin'

spc2_file = base_dir+'/cameradata/spc2_system_latest.log'
spc2_output = base_dir+'/virtualenvs/planktivore/static/system_status/spc2.json'
spcp2_file = base_dir+'/cameradata/spcp2_system_latest.log'
spcp2_output = base_dir+'/virtualenvs/planktivore/static/system_status/spcp2.json'


def add_minute_stats(log,data,camera='SPC2'):
    
    # Add the minute stats entry smooth counts over the last 3 minutes
    dt = datetime.timedelta(minutes=3)
    today = datetime.datetime.now(tz=pytz.utc)

    cam = PlanktonCamera.objects.get(name=camera)
    
    counts = Image.objects.filter(camera__name=cam.name,timestamp__range=[today-dt,today]).count()

    minute_stats = MinuteStats()
    minute_stats.camera = cam
    minute_stats.timestamp = today
    minute_stats.temperature = data['temp1']
    minute_stats.humidity = data['humidity']
    minute_stats.pressure = data['pressure']
    minute_stats.elapsed_time = data['elapsed_sec']
    minute_stats.log_string = log
    minute_stats.camera_active = data['camera_active']
    minute_stats.counts = counts

    # Save
    minute_stats.save()


def parse_log_string(log):

    data = {}
    try:
        data['date'] = log.split(' ')[0]
        data['time'] = log.split(' ')[1]
        data['cleaning'] = log.split(' ')[3].split(',')[8]
        data['temp1'] = float(log.split(' ')[3].split(',')[9])
        data['humidity'] = float(log.split(' ')[3].split(',')[10])
        data['temp2'] = float(log.split(' ')[3].split(',')[11])
        data['pressure'] = float(log.split(' ')[3].split(',')[12].split('\n')[0])
        data['elapsed_sec'] = int(log.split(' ')[3].split(',')[1])
    except:
        data['date'] = ''
        data['time'] = ''
        data['cleaning'] = ''
        data['temp1'] = -1.0
        data['humidity'] = -1.0
        data['temp2'] = -1.0
        data['pressure'] = -1.0
        data['elapsed_sec'] = 0
        pass    

    data['camera_active'] = data['elapsed_sec'] > 60

    return data
       

def run(*args):

    log = open(spc2_file,'r').read()

    data = parse_log_string(log)

    with open(spc2_output, 'w') as outfile:
        json.dump(data,outfile)

    add_minute_stats(log,data,camera='SPC2')

    log = open(spcp2_file,'r').read()

    data = parse_log_string(log)

    with open(spcp2_output, 'w') as outfile:
        json.dump(data,outfile)
    
    add_minute_stats(log,data,camera='SPCP2')
