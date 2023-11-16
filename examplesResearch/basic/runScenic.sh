#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='town02' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
PATHTOCONFIGFILE='examplesResearch/basic/5-mhs-simple.scenic'
USEMHS='True' 

# Simultor variable definitions
###############################
# SIMULATE='-S --model scenic.simulators.carla.model --time 50'
# CARLAMAP="-p carla_map 'Town02'"
# IMGDIR='--image-dir examplesResearch/basic/_output/ego-images'

cmd="poetry run scenic \
-b --count 1 -v 3 \
${SIMULATE} \
${CARLAMAP} \
${IMGDIR} \
-p timeout 30 \
-p evol ${USEMHS} \
-p evol-algo nsga2 \
-p evol-obj actors \
-p evol-NumSols measurement \
-p evol-restart-time -1 \
-p evol-history shallow \
-p no-validation False \
-p outputWS examplesResearch/basic \
-p outputDir _output \
-p viewImgs True \
-p saveImgs True \
-p saveFiles True \
-p saveStats False \
-p map maps/${MAPNAME}.xodr \
${PATHTOCONFIGFILE}"
echo $cmd
eval $cmd
