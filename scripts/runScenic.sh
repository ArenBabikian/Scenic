#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='town02' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
PATHTOCONFIGFILE='measurements/data/tram05/3actors/2-0/d-nsga.scenic'
USENSGA='False' 

# Simultor variable definitions
###############################
SIMULATE='-S --model scenic.simulators.carla.model --time 50'
CARLAMAP="-p carla_map 'Town02'"
IMGDIR='--image-dir meas-temp/dp'

cmd="poetry run scenic \
-b --count 1 -v 0 \
${SIMULATE} \
${CARLAMAP} \
${IMGDIR} \
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