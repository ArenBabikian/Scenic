#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull

# SIMULATE='-S --model scenic.simulators.carla.model'
# IMGDIR='--image-dir config/forFigures/img'


cmd="poetry run scenic \
-b --count 1 -v 3 \
${SIMULATE} \
${IMGDIR}
-p nsga False \
-p nsga-Iters 500 \
-p nsga-NumSols 3 \
-p no-validation False \
-p outputWS config/forFigures \
-p outputDir _ \
-p saveImgs False \
-p viewImgs True \
-p saveFiles True \
-p map maps/town02.xodr \
-p carla_map 'Town02'
config/forFigures/prelim.scenic"
echo $cmd
eval $cmd

