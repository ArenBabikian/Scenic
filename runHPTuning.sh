#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='town02' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
PATHTOCONFIGFILE=$3
USENSGA='True' 

# Simultor variable definitions
###############################
# SIMULATE='-S --model scenic.simulators.carla.model --time 50'
# CARLAMAP="-p carla_map 'Town02'"
# IMGDIR='--image-dir examples/basic/_output/ego-images'

cmd="poetry run scenic \
-b --count 10 -v 0 \
${SIMULATE} \
${CARLAMAP} \
${IMGDIR} \
-p timeout 600 \
-p nsga ${USENSGA} \
-p nsga-NumSols 1 \
-p restart-time -1 \
-p pop_size $1 \
-p num_offspring $2 \
-p no-validation False \
-p outputWS examples/basic \
-p outputDir _output \
-p viewImgs False \
-p saveImgs True \
-p saveFiles True \
-p saveStats True
-p map maps/${MAPNAME}.xodr
${PATHTOCONFIGFILE}"
echo $cmd
eval $cmd