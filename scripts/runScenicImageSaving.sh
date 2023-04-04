#!/usr/bin/env bash
FILENAME="onregion"

python ./scripts/scenicWithImageSaving.py ./meas-temp/dp/$FILENAME-exact.scenic --time 5 --count 1 --res 1920x1080 -o ./meas-temp/dp/$FILENAME --timestep 0.1 -b -S --samplingrate 5

