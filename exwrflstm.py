#!/usr/bin/python

import numpy as np
import pandas as pd
from netCDF4 import Dataset
from datetime import datetime
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import wrf
from wrf import getvar, interplevel
import Image
import matplotlib.patches as mpatches

#setting
#-6.125170, 106.659310
lattarget = -6.125170
lontarget = 106.659310
dirwrf = '/home/genomexyz/WRF/Build_WRF/WPS/skripsi/wrfout/'
frontname = 'wrfout_d03_2016'
backname = ':00:00'
month = "12"
startday = 1
endday = 31
startpred = 13

#note missing data
#september -> wrfout_d03_2016-09-03_00:00:00
#oktober -> wrfout_d03_2016-10-24_12:00:00
#november -> wrfout_d03_2016-11-15_12:00:00'
# wrfout_d03_2016-11-16_00:00:00
# wrfout_d03_2016-11-16_12:00:00
# wrfout_d03_2016-11-17_00:00:00
# wrfout_d03_2016-11-17_12:00:00
# wrfout_d03_2016-11-18_00:00:00
# wrfout_d03_2016-11-18_12:00:00
# wrfout_d03_2016-11-19_00:00:00
# wrfout_d03_2016-11-19_12:00:00
# wrfout_d03_2016-11-20_00:00:00
# wrfout_d03_2016-11-20_12:00:00
# wrfout_d03_2016-11-21_00:00:00
# wrfout_d03_2016-11-21_12:00:00
# wrfout_d03_2016-11-22_00:00:00
# wrfout_d03_2016-11-22_12:00:00
# wrfout_d03_2016-11-23_00:00:00
# wrfout_d03_2016-11-23_12:00:00
# wrfout_d03_2016-11-24_00:00:00
# wrfout_d03_2016-11-24_12:00:00
# wrfout_d03_2016-11-25_00:00:00
# wrfout_d03_2016-11-25_12:00:00
# wrfout_d03_2016-11-26_00:00:00
# wrfout_d03_2016-11-26_12:00:00
# wrfout_d03_2016-11-27_00:00:00
# wrfout_d03_2016-11-27_12:00:00
# wrfout_d03_2016-11-28_00:00:00
# wrfout_d03_2016-11-28_12:00:00

#example
#absvortvar = getvar(dsetwrf, 'avo', timeidx = 12)

#def bilinear_interp(x1, x2, y1, y2, var11, var12, var21, var22):
#	fx1 = (x2-lontarget) / (x2-x1) * var11 + (lontarget-x1) / (x2-x1) * var21
#	fx2 = (x2-lontarget) / (x2-x1) * var12 + (lontarget-x1) / (x2-x1) * var22
#	return (y2-lattarget) / (y2-y1) * fx1 + (lattarget-y1) / (y2-y1) * fx2

def bilinear_interp(x1, x2, y1, y2, var11, var12, var21, var22):
	fx1 = (x2-lontarget) / (x2-x1) * var11 + (lontarget-x1) / (x2-x1) * var21
	fx2 = (x2-lontarget) / (x2-x1) * var12 + (lontarget-x1) / (x2-x1) * var22
	return np.mean([var11, var12, var21, var22])

def rata9():
	

dsetwrf = Dataset('/home/genomexyz/WRF/Build_WRF/WPS/skripsi/wrfout/wrfout_d03_2016-09-01_00:00:00', mode = 'r')

#horizontal grid
latawal = dsetwrf.variables['XLAT'][0]
lonawal = dsetwrf.variables['XLONG'][0]

for i in xrange(len(latawal[:,0])):
	if lattarget > latawal[i,0]:
		y2 = latawal[i,0]
		y1 = latawal[i-1,0]
		titiky2 = i
		titiky1 = i-1

for i in xrange(len(lonawal[0,:])):
	if lontarget > lonawal[0,i]:
		x2 = lonawal[0,i]
		x1 = lonawal[0,i-1]
		titikx2 = i
		titikx1 = i-1

#init container
u850cont = np.asarray([])
u700cont = np.asarray([])
u500cont = np.asarray([])
v850cont = np.asarray([])
v700cont = np.asarray([])
v500cont = np.asarray([])
RH850cont = np.asarray([])
RH700cont = np.asarray([])
RH500cont = np.asarray([])
tc850cont = np.asarray([])
tc700cont = np.asarray([])
tc500cont = np.asarray([])
absvort850cont = np.asarray([])
absvort700cont = np.asarray([])
absvort500cont = np.asarray([])
CAPE = np.asarray([])
precwatercont = np.asarray([])

hujancnt = np.asarray([])

#init missing link
miss = np.asarray([])

#############
#real action#
#############
for day in xrange(startday, endday+1):
	if day < 10:
		daynow = '0'+str(day)
	else:
		daynow = str(day)
	for mode in xrange(2):
		if mode == 0:
			hourdata = "00"
		else:
			hourdata = "12"
		wrfiter = dirwrf+frontname+'-'+month+'-'+daynow+'_'+hourdata+backname
		###############
		#input session#
		###############

		try:
			dsetwrf = Dataset(wrfiter, mode = 'r')
		except IOError:
			print 'lewat', wrfiter
			miss = np.append(miss, wrfiter)
			continue
		print 'sesi', wrfiter
		#horizontal grid
		lat = dsetwrf.variables['XLAT'][0]
		lon = dsetwrf.variables['XLONG'][0]
		
		#get truth variable
		hujan = dsetwrf.variables['RAINNC'][-1] + dsetwrf.variables['RAINC'][-1] + dsetwrf.variables['RAINSH'][-1] \
		- dsetwrf.variables['RAINNC'][startpred] - dsetwrf.variables['RAINC'][startpred] - dsetwrf.variables['RAINSH'][startpred]
		
		hujan[hujan < 0] = 0

		for hour in xrange(13,25):
			#vertical grid (pressure)
			lev = getvar(dsetwrf, "p")
			
			#get core variable
			RHvar = getvar(dsetwrf, "rh", timeidx = hour)
			tcvar = getvar(dsetwrf, "tc", timeidx = hour)
			absvortvar = getvar(dsetwrf, 'avo', timeidx = hour)
			uvar = getvar(dsetwrf, 'ua', timeidx = hour)
			vvar= getvar(dsetwrf, 'va', timeidx = hour)

			#get core var in demand level
			u850 = interplevel(uvar, lev, 85000)
			u700 = interplevel(uvar, lev, 70000)
			u500 = interplevel(uvar, lev, 50000)
			v850 = interplevel(vvar, lev, 85000)
			v700 = interplevel(vvar, lev, 70000)
			v500 = interplevel(vvar, lev, 50000)
			RH850 = interplevel(RHvar, lev, 85000.)
			RH700 = interplevel(RHvar, lev, 70000.)
			RH500 = interplevel(RHvar, lev, 50000.)
			tc850 = interplevel(tcvar, lev, 85000.)
			tc700 = interplevel(tcvar, lev, 70000.)
			tc500 = interplevel(tcvar, lev, 50000.)
			absvort850 = interplevel(absvortvar, lev, 85000.)
			absvort700 = interplevel(absvortvar, lev, 70000.)
			absvort500 = interplevel(absvortvar, lev, 50000.)
			precwater = getvar(dsetwrf, "pw", timeidx = hour)

			u850cont = np.append(u850cont, bilinear_interp(x1, x2, y1, y2, u850[titiky1,titikx1], u850[titiky2,titikx1], \
						u850[titiky1,titikx2], u850[titiky2,titikx2]))
			u700cont = np.append(u700cont, bilinear_interp(x1, x2, y1, y2, u700[titiky1,titikx1], u700[titiky2,titikx1], \
						u700[titiky1,titikx2], u700[titiky2,titikx2]))
			u500cont = np.append(u500cont, bilinear_interp(x1, x2, y1, y2, u500[titiky1,titikx1], u500[titiky2,titikx1], \
						u500[titiky1,titikx2], u500[titiky2,titikx2]))
			v850cont = np.append(v850cont, bilinear_interp(x1, x2, y1, y2, v850[titiky1,titikx1], v850[titiky2,titikx1], \
						v850[titiky1,titikx2], v850[titiky2,titikx2]))
			v700cont = np.append(v700cont, bilinear_interp(x1, x2, y1, y2, v700[titiky1,titikx1], v700[titiky2,titikx1], \
						v700[titiky1,titikx2], v700[titiky2,titikx2]))
			v500cont = np.append(v500cont, bilinear_interp(x1, x2, y1, y2, v500[titiky1,titikx1], v500[titiky2,titikx1], \
						v500[titiky1,titikx2], v500[titiky2,titikx2]))
			RH850cont = np.append(RH850cont, bilinear_interp(x1, x2, y1, y2, RH850[titiky1,titikx1], RH850[titiky2,titikx1], \
						RH850[titiky1,titikx2], RH850[titiky2,titikx2]))
			RH700cont = np.append(RH700cont, bilinear_interp(x1, x2, y1, y2, RH700[titiky1,titikx1], RH700[titiky2,titikx1], \
						RH700[titiky1,titikx2], RH700[titiky2,titikx2]))
			RH500cont = np.append(RH500cont, bilinear_interp(x1, x2, y1, y2, RH500[titiky1,titikx1], RH500[titiky2,titikx1], \
						RH500[titiky1,titikx2], RH500[titiky2,titikx2]))
			tc850cont = np.append(tc850cont, bilinear_interp(x1, x2, y1, y2, tc850[titiky1,titikx1], tc850[titiky2,titikx1], \
						tc500[titiky1,titikx2], tc500[titiky2,titikx2]))
			tc700cont = np.append(tc700cont, bilinear_interp(x1, x2, y1, y2, tc700[titiky1,titikx1], tc700[titiky2,titikx1], \
						tc700[titiky1,titikx2], tc700[titiky2,titikx2]))
			tc500cont = np.append(tc500cont, bilinear_interp(x1, x2, y1, y2, tc500[titiky1,titikx1], tc500[titiky2,titikx1], \
						tc500[titiky1,titikx2], tc500[titiky2,titikx2]))
			absvort850cont = np.append(absvort850cont, bilinear_interp(x1, x2, y1, y2, absvort850[titiky1,titikx1], absvort850[titiky2,titikx1], \
						absvort850[titiky1,titikx2], absvort850[titiky2,titikx2]))
			absvort700cont = np.append(absvort700cont, bilinear_interp(x1, x2, y1, y2, absvort700[titiky1,titikx1], absvort700[titiky2,titikx1], \
						absvort700[titiky1,titikx2], absvort700[titiky2,titikx2]))
			absvort500cont = np.append(absvort500cont, bilinear_interp(x1, x2, y1, y2, absvort500[titiky1,titikx1], absvort500[titiky2,titikx1], \
						absvort500[titiky1,titikx2], absvort500[titiky2,titikx2]))
			precwatercont = np.append(precwatercont, bilinear_interp(x1, x2, y1, y2, precwater[titiky1,titikx1], precwater[titiky2,titikx1], \
						precwater[titiky1,titikx2], precwater[titiky2,titikx2]))
		hujancek = bilinear_interp(x1, x2, y1, y2, hujan[titiky1,titikx1], hujan[titiky2,titikx1], hujan[titiky1,titikx2], hujan[titiky2,titikx2])
		if hujancek < 0:
			hujancek = 0
		hujancnt = np.append(hujancnt, hujancek)

#save extract to csv file
df = pd.DataFrame({"v850" : v850cont, "v700" : v700cont, "v500" : v500cont, "u850" : u850cont, "u700" : u700cont, "u500" : u500cont, \
					"RH850" : RH850cont, "RH700" : RH700cont, "RH500" : RH500cont, "tc850" : tc850cont, "tc700" : tc700cont, \
					"tc500" : tc500cont, "absvort850" : absvort850cont, "absvort700" : absvort700cont, "absvort500" : absvort500cont, \
					"precwater" : precwatercont})
df.to_csv("skripsihujanasli12.csv", index=False)

dfout = pd.DataFrame({"hujan" : hujancnt})
dfout.to_csv("skripsihujanasli12o.csv", index=False)

print 'missing data:'
print miss
