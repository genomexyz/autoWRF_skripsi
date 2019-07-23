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
import sys

#setting
#-6.697995, 106.934937
lattarget = -6.697995
lontarget = 106.934937
dirwrf = '/media/genomexyz/Seagate/aa/bogor3bulan/'
frontname = 'wrfout_d03_2017'
backname = ':00:00'
month = "01"
startday = 1
endday = 31
startpred = 13
hour = 15

#note missing data
#Februari -> wrfout_d03_2018-02-07_12:00:00
#wrfout_d03_2018-02-10_00:00:00

#example
#absvortvar = getvar(dsetwrf, 'avo', timeidx = 12)

#def bilinear_interp(x1, x2, y1, y2, var11, var12, var21, var22):
#	fx1 = (x2-lontarget) / (x2-x1) * var11 + (lontarget-x1) / (x2-x1) * var21
#	fx2 = (x2-lontarget) / (x2-x1) * var12 + (lontarget-x1) / (x2-x1) * var22
#	return (y2-lattarget) / (y2-y1) * fx1 + (lattarget-y1) / (y2-y1) * fx2

def rata4(x1, x2, y1, y2, var11, var12, var21, var22):
	fx1 = (x2-lontarget) / (x2-x1) * var11 + (lontarget-x1) / (x2-x1) * var21
	fx2 = (x2-lontarget) / (x2-x1) * var12 + (lontarget-x1) / (x2-x1) * var22
	return np.nanmean([var11, var12, var21, var22])


#check arg
#arg is hour(int) month (string) year (string)
hour = int(sys.argv[1])
month = sys.argv[2]
year = sys.argv[3]


dsetwrf = Dataset('/media/genomexyz/Seagate/aa/bogor3bulan/wrfout_d03_2017-12-01_00:00:00', mode = 'r')

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

#init missing link
miss = np.asarray([])

#init container
CAPEcont = np.asarray([])
CINcont = np.asarray([])
LCLcont = np.asarray([])
LFCcont = np.asarray([])
KIcont = np.asarray([])
VTcont = np.asarray([])
CTcont = np.asarray([])
RHcont = np.asarray([])
Tcont = np.asarray([])
hujancont = np.asarray([])
TTcont = np.asarray([])

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

#level that needed
#850, 700, 500
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

		#vertical grid (pressure)
		lev = getvar(dsetwrf, "p")
		#get core variable
		RHvar = getvar(dsetwrf, "rh", timeidx = hour)
		Tvar = getvar(dsetwrf, "tc", timeidx = hour)
		Tdvar = getvar(dsetwrf, "td", timeidx = hour)
		CCILFLC = getvar(dsetwrf, "cape_2d", timeidx = hour)
		CAPEvar = CCILFLC[0]
		CINvar = CCILFLC[1]
		LFCvar = CCILFLC[2]
		LCLvar = CCILFLC[3]
		hujanvar = dsetwrf.variables['RAINNC'][-1] + dsetwrf.variables['RAINC'][-1] + dsetwrf.variables['RAINSH'][-1] \
		- dsetwrf.variables['RAINNC'][12] - dsetwrf.variables['RAINC'][12] - dsetwrf.variables['RAINSH'][12]
		
		hujanvar[hujanvar < 0] = 0

		#get core var in demand level
		RH700 = interplevel(RHvar, lev, 70000)
		T850 = interplevel(Tvar, lev, 85000)
		T700 = interplevel(Tvar, lev, 70000)
		T500 = interplevel(Tvar, lev, 50000)
		Td850 = interplevel(Tdvar, lev, 85000)
		Td700 = interplevel(Tdvar, lev, 70000)
		Td500 = interplevel(Tdvar, lev, 50000)

		#get index
		KI = (T850 - T500) + Td850 - (T700 - Td700)
		VT = T850 - T500
		CT = Td850 - T500
		TT = VT + CT

		KIcont = np.append(KIcont, rata4(x1, x2, y1, y2, KI[titiky1,titikx1], \
		KI[titiky2,titikx1], KI[titiky1,titikx2], KI[titiky2,titikx2]))
		
		VTcont = np.append(VTcont, rata4(x1, x2, y1, y2, VT[titiky1,titikx1], \
		VT[titiky2,titikx1], VT[titiky1,titikx2], VT[titiky2,titikx2]))
		
		CTcont = np.append(CTcont, rata4(x1, x2, y1, y2, CT[titiky1,titikx1], \
		CT[titiky2,titikx1], CT[titiky1,titikx2], CT[titiky2,titikx2]))
		#print titiky1,titikx2
		#print  np.asarray(Td850[13,27]), np.asarray(Td850[13,25]), np.asarray(Td850[13,26]), np.asarray(Td850[13,39])
		
		CAPEcont = np.append(CAPEcont, rata4(x1, x2, y1, y2, CAPEvar[titiky1,titikx1], \
		CAPEvar[titiky2,titikx1], CAPEvar[titiky1,titikx2], CAPEvar[titiky2,titikx2]))
		
		CINcont = np.append(CINcont, rata4(x1, x2, y1, y2, CINvar[titiky1,titikx1], \
		CINvar[titiky2,titikx1], CINvar[titiky1,titikx2], CINvar[titiky2,titikx2]))
		
		LFCcont = np.append(LFCcont, rata4(x1, x2, y1, y2, LFCvar[titiky1,titikx1], \
		LFCvar[titiky2,titikx1], LFCvar[titiky1,titikx2], LFCvar[titiky2,titikx2]))
		
		LCLcont = np.append(LCLcont, rata4(x1, x2, y1, y2, LCLvar[titiky1,titikx1], \
		LCLvar[titiky2,titikx1], LCLvar[titiky1,titikx2], LCLvar[titiky2,titikx2]))
		
		Tcont = np.append(Tcont, rata4(x1, x2, y1, y2, T700[titiky1,titikx1], \
		T700[titiky2,titikx1], T700[titiky1,titikx2], T700[titiky2,titikx2]))
		
		TTcont = np.append(TTcont, rata4(x1, x2, y1, y2, TT[titiky1,titikx1], \
		TT[titiky2,titikx1], TT[titiky1,titikx2], TT[titiky2,titikx2]))
		
		RHcont = np.append(RHcont, rata4(x1, x2, y1, y2, RH700[titiky1,titikx1], \
		RH700[titiky2,titikx1], RH700[titiky1,titikx2], RH700[titiky2,titikx2]))
		
		hujancont = np.append(hujancont, rata4(x1, x2, y1, y2, hujanvar[titiky1,titikx1], \
		hujanvar[titiky2,titikx1], hujanvar[titiky1,titikx2], hujanvar[titiky2,titikx2]))
#		CAPEcont = 

#save data
dfout = pd.DataFrame({"hujan": hujancont,"KI" : KIcont, "VT" : VTcont, "CT" : CTcont, "T" : Tcont, "RH" : RHcont})
dfout.to_csv("risetCPNN/training data/"+month+year+"-"+str(24-hour)+".csv", index=False)
#dfout.to_csv("risetCPNN/training data/cobaaja.csv", index=False)
#save data
#dfout = pd.DataFrame({"KI" : KIcont,"TT" : TTcont, "T" : Tcont, "RH" : RHcont})
#dfout.to_csv("paper2019prediktor-122017.csv", index=False)

print RHcont
