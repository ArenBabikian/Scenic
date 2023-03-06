#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='zalaFullcrop' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
PATHTOCONFIGFILE='measurements/data/zalaFullcrop/2actors/0-0/d-nsga.scenic'
USENSGA='True' 

# Simultor variable definitions
###############################
# SIMULATE='-S --model scenic.simulators.carla.model --time 50'
# CARLAMAP="-p carla_map 'Town02'"
# IMGDIR='--image-dir examples/basic/_output/ego-images'

cmd="poetry run scenic \
-b --count 1 -v 3 \
${SIMULATE} \
${CARLAMAP} \
${IMGDIR} \
-p timeout 30 \
-p evol ${USENSGA} \
-p evol-algo nsga \
-p nsga-Iters 500 \
-p nsga-NumSols 1 \
-p restart-time -1
-p no-validation False \
-p outputWS meas-temp \
-p outputDir _output \
-p viewImgs True \
-p saveImgs True \
-p saveFiles True \
-p saveStats True
-p map maps/${MAPNAME}.xodr
${PATHTOCONFIGFILE}"
echo $cmd
eval $cmd