#!/usr/bin/env bash

cmd="poetry run scenic -b --count 1 -v 3 \
-p nsga True \
-p iterations 100 \
-p selBest True \
`#-p savePath test` \
-p map \"../maps/CARLA/Town02.xodr\" \
../config/run.scenic"
eval $cmd