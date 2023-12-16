#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='tram05-mod'
PATHTOCONFIGFILE='issta/config/dummy1.scenic' # town10HD
USENSGA='True'

cmd="poetry run scenic \
-b --count 1 -v 2 \
--zoom 0 \
-p evol False \
-p no-validation True \
-p viewImgs True \
-p saveImgs False \
-p saveFiles False \
-p showPaths False \
-p savePaths False \
-p saveStats False \
-p map maps/${MAPNAME}.xodr \
${PATHTOCONFIGFILE}"
echo $cmd
eval $cmd


# -p static-element-at [0,5] \
