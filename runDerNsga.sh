#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull

config="3actors"

cmd="poetry run scenic \
-b --count 1 -v 3 \
-p nsga True \
-p nsga-Iters 300 \
-p nsga-NumSols 1 \
-p no-validation False \
-p outputWS out-nsga \
-p outputDir _ \
-p saveImgs False \
-p saveFiles False \
measurements/${config}/0-0-d-nsga.scenic"
eval $cmd