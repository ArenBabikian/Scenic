#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull

#-p no-validation True

cmd="poetry run scenic \
-b --count 1 -v 3 \
-p nsga True \
-p nsga-Iters 500 \
-p nsga-NumSols 2 \
-p savePath nsga-out \
-p saveImgs True \
-p saveFiles True \
../config/generatednew.scenic"
eval $cmd