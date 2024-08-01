#!/bin/bash
# shellcheck disable=SC2154

set -e

source "$(dirname "$0")"/koi

koiname=$0
koidescription="Combine in time split in var"

function __koimain {
    __addarg "-h" "--help" "help" "optional" "" "$koidescription" ""
    __addarg "-p" "--prefix" "storevalue" "required" "" "Prefix" ""
    __addarg "" "ifiles" "positionalarray" "required" "" "WRF output files" ""
    __parseargs "$@"

    cdoInputs=""
    for ffile in "${ifiles[@]}"; do
        sc=$(echo "$ffile" | rev | cut -c1-2 | rev)
        mn=$(echo "$ffile" | rev | cut -c4-5 | rev)
        hr=$(echo "$ffile" | rev | cut -c7-8 | rev)
        dd=$(echo "$ffile" | rev | cut -c10-11 | rev)
        mm=$(echo "$ffile" | rev | cut -c13-14 | rev)
        yyyy=$(echo "$ffile" | rev | cut -c16-19 | rev)
        dateStamp=${yyyy}-${mm}-${dd},${hr}:${mn}:${sc}
        cdoInputs="$cdoInputs -settaxis,$dateStamp,1hour $ffile"
    done
    cdo -r -splitvar -mergetime $cdoInputs $prefix 
}

__koirun "$@"
