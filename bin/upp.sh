#!/bin/bash
# shellcheck disable=SC2154

set -eu

UPP_DIR=${UPP_DIR:-$SKRIPS_DIR/external/UPPV4.0.1}

if [ $# -eq 0 ]; then
	echo "No prefixes provided."
	exit 1
fi

njobs=0
for prefix in "$@"; do
	for i in "${prefix}"_d01_*; do
		run_upp -u "$UPP_DIR" \
			-c "$PARM_DIR"/upp/postxconfig-"${prefix}".txt \
			-i "$i" \
			-r "$run_cmd" &
		njobs=$((njobs + 1))
		if [ $njobs -ge "$max_par_jobs" ]; then
			echo submitted 10 jobs.... waiting..
			wait
			njobs=0
		fi
	done
done
wait

for prefix in "$@"; do
	grib_copy "${prefix}"*.grib2 'wrf_[typeOfLevel]_[shortName].grb2'
	rm "${prefix}"*.grib2
done
