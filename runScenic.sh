#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull


cmd="poetry run scenic \
-b --count 1 -v 3 \
-p nsga False \
-p nsga-Iters 500 \
-p nsga-NumSols 3 \
-p no-validation False \
-p outputWS out-nsga \
-p outputDir _ \
-p saveImgs False \
-p viewImgs True \
-p saveFiles False \
-p map maps/zalaFullCrop.xodr
../config/run.scenic"
eval $cmd