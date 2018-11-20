#!/usr/bin/env python
from datetime import datetime
import json
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['ytick.direction'] = 'in'
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['font.size'] = 12

def toDateTime(epoch): # convert from DD/MM/YY
    if len(epoch.split()) == 1:
        epoch += 'T00:00:00'
    else:
        epoch = 'T'.join(epoch.split())
    d, t = epoch.split('T')
    dd, mm, yy = d.split('/')
    epoch = '20{}-{}-{}T{}'.format(yy, mm, dd, t)
    return np.datetime64(epoch)

# releases
with open('mantidversions.json') as handle:
    doc = json.load(handle)
releases = {}
for item in doc:
    releases[item['tag_name']] = np.datetime64(item['published_at'])

# tags that aren't releases
for item in ['v2.4', 'v2.3.2', 'v2.3.1', 'v2.3', 'v2.2', 'v2.1.1', 'v2.1', 'v2.0.2', 'v2.0.1', 'v2.0', 'Iteration30']:
    if item in releases.keys():
        continue
    releases[item] = None

releases['Iteration0'] = toDateTime('07/09/07') # pilot

# add earlier iterations
doc = ['05/10/07', '02/11/07', '30/11/07', '04/01/08', '01/02/08', '17/03/08', '07/04/08',
       '22/05/08', '27/06/08', '27/06/08', '05/09/08', '03/10/08', '30/10/08', '19/12/08',
       '06/02/09', '06/03/09', '15/05/09', '26/06/09', '01/08/09', '26/11/09 13:38:04',
       '10/02/10 12:33:01', '08/04/10 08:44:59', '15/06/10 15:38:35', '27/08/10 13:02:12',
       '05/11/10 12:14:39', '20/12/10 10:51:47', '18/02/11', '06/05/11', '01/07/11', '23/09/11']
for i, epoch in enumerate(doc):
    releases['Iteration{}'.format(i+31-len(doc))] = toDateTime(epoch)

# add specific dates DD/MM/YY
releases['v2.0'] = toDateTime('03/02/12')
releases['v2.0.2'] = toDateTime('16/03/12')
releases['v2.1'] = toDateTime('04/05/12')
del releases['v2.0.1']
releases['v2.1.1'] = toDateTime('01/06/12')
releases['v2.2'] = toDateTime('13/08/12')
releases['v2.3'] = toDateTime('02/11/12')
releases['v2.3.1'] = toDateTime('21/11/12')
releases['v2.3.2'] = toDateTime('12/12/12')
releases['v2.4'] = toDateTime('04/02/13')

# convert to lists
keys = list(releases.keys())
keys.sort()
versions = []
epochs = []
for version in keys:
    epochs.append(releases[version].astype(datetime))
    if version.startswith('Iteration'):
        version = float(version.replace('Iteration', ''))
    elif version.startswith('v'):
        version = version[1:]
        version = version.split('.')
        if len(version) == 2:
            version.append(0)
        version = float(version[0]) + .01*float(version[1]) + .001 * float(version[2])
    versions.append(version)

versions = np.asarray(versions)
epochs = np.asarray(epochs)

years = np.asarray([np.datetime64('2007-01-01').astype(datetime),
         np.datetime64('2009-01-01').astype(datetime),
         np.datetime64('2011-01-01').astype(datetime),])

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')
fig, axes = plt.subplots(ncols=3,
                         gridspec_kw={'width_ratios':[(2012-2007),
                                                      (2014-2012),
                                                      (2019-2014)]})
for ax in axes:
    ax.plot_date(epochs, versions)
    #ax.set_xticks(years)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(yearsFmt)
axes[0].set_ylabel('Mantid version')
axes[0].set_xlim(np.datetime64('2007-08-01').astype(datetime),
                 np.datetime64('2011-10-01').astype(datetime))
axes[1].set_xlim(np.datetime64('2011-10-01').astype(datetime),
                 np.datetime64('2013-11-01').astype(datetime))
axes[1].set_ylim(1.998, 2.063)
axes[2].set_xlim(np.datetime64('2013-11-01').astype(datetime),
                 np.datetime64('2019-01-01').astype(datetime))
axes[2].set_ylim(2.997, 3.135)
fig.set_tight_layout(True)
fig.show()
