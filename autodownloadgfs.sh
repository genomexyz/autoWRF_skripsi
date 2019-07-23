#!/bin/bash

#setting
savedir="/home/genomexyz/WRF/Build_WRF/DATA/skripsi"
forecasttot=4
forecasttimestep=3
year=2016
month=5
startday=3
endday=31
starthour=0

#if [ $# -lt 4 ]
#then
#	echo "usage: ./autodownloadgfs.sh month startday endday nextmonth(opt)"
#	echo "last argument is optional"
#	exit
#fi

#if (( $3 > $4 ))
#then
#	echo "usage: ./autodownloadgfs.sh month startday endday nextmonth(opt)"
#	echo "last argument is optional"
#	echo $2 $3
#	exit
#else
#	year=$1
#	month=$2
#	startday=$3
#	endday=$(($4+1))
#fi

#if [[ $4 == "end" ]]
#then
#	endmonth="active"
#fi

#if (( $i == $endday ))
#then
#	hari=01
#	month=$(($month+1))
#fi

echo $endmonth

for ((i=$(($startday)); i<=$endday; i++)); do
	for ((j=0; j<2; j++)); do
		if (( $i < 10 ))
		then
			hari=0$i
		else
			hari=$i
		fi

		if (( $month < 10 ))
		then
			bulan=0$month
		else
			bulan=$month
		fi

		if (( $j == 0 ))
		then
			mode="_0000_"
		else
			mode="_1200_"
		fi
		wget --directory-prefix="$savedir" "https://nomads.ncdc.noaa.gov/data/gfs4/""$year$bulan"/"$year$bulan$hari"/gfs_4_"$year$bulan$hari$mode"000.grb2
		wget --directory-prefix="$savedir" "https://nomads.ncdc.noaa.gov/data/gfs4/""$year$bulan"/"$year$bulan$hari"/gfs_4_"$year$bulan$hari$mode"003.grb2
		wget --directory-prefix="$savedir" "https://nomads.ncdc.noaa.gov/data/gfs4/""$year$bulan"/"$year$bulan$hari"/gfs_4_"$year$bulan$hari$mode"006.grb2
		wget --directory-prefix="$savedir" "https://nomads.ncdc.noaa.gov/data/gfs4/""$year$bulan"/"$year$bulan$hari"/gfs_4_"$year$bulan$hari$mode"009.grb2
		wget --directory-prefix="$savedir" "https://nomads.ncdc.noaa.gov/data/gfs4/""$year$bulan"/"$year$bulan$hari"/gfs_4_"$year$bulan$hari$mode"012.grb2
	done
done
