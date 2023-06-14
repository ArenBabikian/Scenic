#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='town10HD' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
PATHTOCONFIGFILE='measurements/data/tram05/2actors/2-0/d-nsga.scenic'
PATHTOCONFIGFILE='examplesResearch/mapAbstraction/town10HD.scenic'
USENSGA='True'
# PATHTOCONFIGFILE='examplesResearch/other/explore_map.scenic'
# USENSGA='False'

cmd="poetry run scenic \
-b --count 1 -v 0 \
-p timeout 30 \
-p evol ${USENSGA} \
-p evol-algo nsga3 \
-p evol-obj categories \
-p evol-NumSols measurement \
-p evol-restart-time -1 \
-p evol-history shallow \
-p no-validation True \
-p outputWS meas-temp \
-p outputDir _output \
-p viewImgs True \
-p saveImgs False \
-p saveFiles False \
-p saveStats False \
-p map maps/${MAPNAME}.xodr \
${PATHTOCONFIGFILE}"
echo $cmd
eval $cmd