#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='town02' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
PATHTOCONFIGFILE='measurements/data/tram05/3actors/2-0/d-nsga.scenic'
PATHTOCONFIGFILE='meas-temp/dynamic/exact.scenic'
PATHTOCONFIGFILE='measurements/data/tram05/4actors/7-0/d-nsga.scenic'
USENSGA='False' 

# Simultor variable definitions
###############################
SIMULATION="-S \
--model scenic.simulators.carla.model \
--time 50 \
--max-sims-per-scene 1 \
-p sim-saveDir meas-temp/dynamic
-p sim-saveStats True \
-p render 0 \
--show-records \
"
# SIMULATION+=" -p carla_map 'Town02'"

cmd="poetry run scenic \
-b --count 1 -v 0 \
${SIMULATION} \
-p timeout 30 \
-p evol ${USENSGA} \
-p evol-algo nsga2 \
-p evol-obj categImpo \
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