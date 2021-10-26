#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull

config="3actors"
map="tram05"

cmd="poetry run scenic \
-b --count 1 -v 3 \
-p nsga False \
-p measure True \
-p outputWS measurements \
-p outputDir ${config} \
-p saveImgs True \
-p saveFiles True \
-p map ../maps/${map}.xodr
measurements/config/${config}.scenic"
eval $cmd
# measurements/3actors/0-0-exact.scenic