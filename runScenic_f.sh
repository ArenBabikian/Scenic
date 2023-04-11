#!/usr/bin/env bash

# General variable definitions
##############################
MAPNAME='tram05' #'town02', 'tram05', 'tram05-mod', 'zalaFullcrop'
PATHTOCONFIGFILE='examples/basic/pb-maps-tests/14-distfar-test.scenic'
USENSGA='True' 

# Simultor variable definitions
###############################
# SIMULATE='-S --model scenic.simulators.carla.model --time 50'
# CARLAMAP="-p carla_map 'Town02'"
# IMGDIR='--image-dir examples/basic/_output/ego-images'

cmd="poetry run scenic \
-b --count 50 -v 1 \
${SIMULATE} \
${CARLAMAP} \
${IMGDIR} \
-p timeout 30 \
-p nsga ${USENSGA} \
-p nsga-Iters 500 \
-p nsga-NumSols 1 \
-p restart-time -1
-p no-validation False \
-p outputWS examples/basic \
-p outputDir _output \
-p viewImgs False \
-p saveImgs False \
-p saveFiles False \
-p saveStats True
-p map maps/${MAPNAME}.xodr
${PATHTOCONFIGFILE}"
echo $cmd
eval $cmd