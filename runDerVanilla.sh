#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull
config="3actors"

cmd="poetry run scenic \
-b --count 1 -v 3 \
-p nsga False \
-p nsga-Iters 100 \
-p nsga-NumSols 3 \
-p no-validation False \
-p outputWS out-nsga \
-p outputDir _ \
-p saveImgs False \
-p saveFiles False \
measurements/${config}/0-0-d-sc3.scenic"
eval $cmd