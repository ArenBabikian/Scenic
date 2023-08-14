#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='town05' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
# MAPNAME='tram05'
PATHTOCONFIGFILE='measurements/data/tram05/2actors/2-0/d-nsga.scenic'
PATHTOCONFIGFILE='examplesResearch/mapAbstraction/intersection.scenic' # town10HD
# PATHTOCONFIGFILE='examplesResearch/mapAbstraction/testing.scenic' # town10HD
PATHTOCONFIGFILE='examplesResearch/mapAbstraction/simpler_test.scenic' # town10HD
PATHTOCONFIGFILE='examplesResearch/mapAbstraction/_mbc-simple.scenic' # town10HD
USENSGA='True'
# # PATHTOCONFIGFILE='examplesResearch/other/explore_map.scenic'
# PATHTOCONFIGFILE='examplesResearch/mapAbstraction/exact-rd.scenic'
# # PATHTOCONFIGFILE='examplesResearch/mapAbstraction/exact-tram.scenic'
# USENSGA='False'

cmd="poetry run scenic \
-b --count 1 -v 2 \
--zoom 0 \
-p timeout 30 \
-p evol ${USENSGA} \
-p evol-algo nsga2 \
-p evol-obj actors \
-p evol-NumSols measurement \
-p evol-restart-time -1 \
-p evol-history shallow \
-p no-validation True \
-p outputWS meas-temp \
-p outputDir _output \
-p viewImgs True \
-p saveImgs False \
-p saveFiles False \
-p viewPaths True \
-p savePaths True \
-p saveStats False \
-p map maps/${MAPNAME}.xodr \
${PATHTOCONFIGFILE}"
echo $cmd
eval $cmd