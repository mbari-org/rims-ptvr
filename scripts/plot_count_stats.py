import numpy as np
from dateutil import parser
import matplotlib.pyplot as plt

from rois.models import Image

import datetime

def run(*args):
    d1 = parser.parse('2024-03-20 19:00:00 UTC')
    d2 = parser.parse('2024-03-21 19:00:00 UTC')

    total_minutes = int((d2 - d1).total_seconds()/60)

    counts = []
    timestamp = []

    for i in range(0,total_minutes):
        da = d1 + datetime.timedelta(minutes=i)
        db = da + datetime.timedelta(minutes=1)
        count = Image.objects.filter(timestamp__range=[da,db]).count()
        counts.append(count)
        timestamp.append(db)
        print([db,count])
        
    fig, ax = plt.subplots()

    #print(counts)

    plt.xticks(rotation=25)
    ax.plot(timestamp,counts)

    plt.savefig('counts.png')