#!/usr/bin/env bash

# SIMULATE='-S --model scenic.simulators.carla.model'
# IMGDIR='--image-dir config/forFigures/img'

cmd="poetry run scenic \
-b --count 10 -v 1 \
${SIMULATE} \
${IMGDIR} \
-p nsga True \
-p nsga-NumSols 1 \
-p restart-time -1 \
-p timeout 300 \
-p outputWS meas-off/Attila \
-p outputDir results/$1 \
-p saveImgs True \
-p viewImgs False \
-p saveFiles True \
-p map maps/tram05-mod.xodr \
meas-off/Attila/scenes/$1.scenic"
echo $cmd
eval $cmd

