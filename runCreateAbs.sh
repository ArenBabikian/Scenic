#!/usr/bin/env bash

# CARLA/Town02
# tram05
# ZalaFull

config="2actors"
map="tram05"

cmd="poetry run scenic \
-b --count 20 -v 3 \
-p nsga False \
-p getAbsScene True \
-p outputWS measurements/data \
-p outputDir ${map}/${config} \
-p saveImgs True \
-p saveFiles True \
-p map ../maps/${map}.xodr
measurements/config/${config}.scenic"
eval $cmd
# measurements/3actors/0-0-exact.scenic