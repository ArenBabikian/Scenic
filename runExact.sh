#!/usr/bin/env bash


# SIMULATE='-S --model scenic.simulators.carla.model'
# IMGDIR='--image-dir config/forFigures/img'
CARLAMAP="-p carla_map 'Town02'"

cmd="poetry run scenic \
-b --count 1 -v 2 \
${SIMULATE} \
${IMGDIR} \
${CARLAMAP} \
-p outputWS config/forFigures \
-p outputDir _ \
-p saveImgs False \
-p viewImgs True \
-p saveFiles False \

config/forFigures/_/0-0/exact.scenic"
echo $cmd
eval $cmd

