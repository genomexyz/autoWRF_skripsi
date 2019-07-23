#!/bin/bash

#########
#setting#
#########
WRFworkdir="/home/genomexyz/WRF/Build_WRF/"
WPS="WPS/"
WPSdomain="palu/"
WRFARWrun="WRFV3/run/"
gfsdir=/mnt/Seagate/skripsi/dataGFS/skripsi
#time adjustment
timemode2="_12:00:00"
timemode1="_00:00:00"
tahun=2016
month=1
startday=9
endday=9

if [ $# -lt 4 ]
then
	echo "usage: ./autorunwrf.sh year month startday endday isthereanextmonth(end)"
	echo "last argument is optional"
	exit
fi

if (( $3 > $4 ))
then
	echo "usage: ./autorunwrf.sh year month startday endday isthereanextmonth(end)"
	echo "last argument is optional"
	echo $2 $3
	exit
else
	tahun=$1
	month=$2
	startday=$3
	endday=$4
fi

if [[ $5 == "end" ]]
then
	endmonth="active"
fi
for ((j=$(($startday)); j<=$endday; j++)); do
	for ((k=0; k<2; k++)); do
#numbering purpose
		if (( $month < 10 )); then
			bulan=0$month
		else
			bulan=$month
		fi
		if (( $j < 10 )); then
			hari=0$j
		else
			hari=$j
		fi

		if (( $k == 0 )); then
			gfsdata="_0000_"
			bulan2=$bulan
			hourinput=0
			hourWPS=$timemode1
			hourWPS2=$timemode1
			if ((  $(($j+1)) < 10 )); then
				hari2=0$(($j+1))
			else
				hari2=$(($j+1))
			fi
		else
			gfsdata="_1200_"
			hourinput=12
			hourWPS=$timemode2
			hourWPS2=$timemode2
			if ((  $(($j+1)) < 10 )); then
				hari2=0$(($j+1))
			else
				hari2=$(($j+1))
			fi
			if (( $5 == "end" ))
			then
				if (( $(($j+1)) > endday ))
				then
					hari2=01
					if (( $month < 9 )); then
						bulan2=0$(($month+1))
					else
						bulan2=$(($month+1))
					fi
				else
					bulan2=$bulan
				fi
			else
				bulan2=$bulan
			fi
		fi

		#edit namelist
		startdate=" start_date = '$tahun-$bulan-$hari$hourWPS', '$tahun-$bulan-$hari$hourWPS', '$tahun-$bulan-$hari$hourWPS',"
		enddate=" end_date   = '$tahun-$bulan2-$hari2$hourWPS2', '$tahun-$bulan2-$hari2$hourWPS2', '$tahun-$bulan2-$hari2$hourWPS2',"
		sed -i "4s/.*/$startdate/" namelist.wps
		sed -i "5s/.*/$enddate/" namelist.wps

		sed -i "6s/.*/ start_year               = $tahun,     $tahun,     $tahun,/" namelist.input
		sed -i "7s/.*/ start_month              = $bulan,       $bulan,       $bulan,/" namelist.input
		sed -i "8s/.*/ start_day                = $hari,        $hari,        $hari,/" namelist.input
		sed -i "9s/.*/ start_hour               = $hourinput,       $hourinput,       $hourinput,/" namelist.input
		sed -i "12s/.*/ end_year                 = $tahun,     $tahun,     $tahun,/" namelist.input
		sed -i "13s/.*/ end_month                = $bulan2,       $bulan2,       $bulan2,/" namelist.input
		sed -i "14s/.*/ end_day                  = $hari2,        $hari2,        $hari2,/" namelist.input
		sed -i "15s/.*/ end_hour                 = $hourinput,        $hourinput,        $hourinput,/" namelist.input


#RUNNING WPS
		#time ./geogrid.exe
		#ln -s $WRFworkdir$WPS"ungrib/Variable_Tables/Vtable.GFS" $WRFworkdir$WPS$WPSdomain"Vtable"
		#$WRFworkdir$WPS"link_grib.csh" "$gfsdir/"gfs_4_$tahun$bulan$hari$gfsdata
		./link_grib.csh "$gfsdir/"gfs_4_$tahun$bulan$hari$gfsdata
		time ./ungrib.exe
		time ./metgrid.exe
#RUNNING WRF
		#cd $WRFworkdir$WRFARWrun
		#ln -sf /home/genomexyz/WRF/Build_WRF/WPS/palu/namelist* .
		#ln -sf /home/genomexyz/WRF/Build_WRF/WPS/palu/met_em* .
		time mpirun -np 4 ./real.exe
		time mpirun -np 4 ./wrf.exe
#cleaning
		rm -f met_em*
		#cd $WRFworkdir$WPS$WPSdomain
		rm -f met_em*
		rm -f FILE:*
	done
done
