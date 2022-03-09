#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull


cmd="poetry run scenic \
-b --count 1 -v 3 \
-p timeout 60 \
-p nsga False \
-p nsga-Iters 500 \
-p nsga-NumSols 3 \
-p no-validation False \
-p outputWS out-oszkar \
-p outputDir _ \
-p saveImgs False \
-p viewImgs True \
-p saveFiles False \
-p map maps/Town02.xodr
config/figForOszkar.scenic"
eval $cmd