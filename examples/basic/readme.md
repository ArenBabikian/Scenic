# Getting started with this repo
Use the scene specification files in this folder to get started with this repo.

## How to run the scene specification files
* The best way to get started with this repo is to run the `runScenic.sh` file by using the command `bash runScenic.sh` while in the root directory.
* `runScenic.sh` contains a few customizable variables such as `MAPNAME`, `PATHTOCONFIGFILE` and `USENSGA`:
  * You can change the `PATHTOCONFIGFILE` variable to point to the scene you want to run
  * The `USENSGA` variable specifies whether you want to use vanilla _Scenic_ (`USENSGA=False`), or whether you want to use the novel _NSGA_ approach implemented in this repo (`USENSGA=True`). 
  * __NOTE 1:__ when `USENSGA=True`, make sure you are running a nsga-compatible scene specification. nsga-compatible means that the file name contains "nsga" (this is a coincidence for this directory, it is not checked by the program).
  * __NOTE 2:__ when `USENSGA` is enabled, the program considers the constraints specified within the `param constraints` variable of the scene specification file. Otherwise, the variable value is ignored, and the remainder of the document is considered. This is not entirely true, but it is true enough to get started.
  * You can also play around with some of the other command line arguments, but this may not be very relevant.

## About the scene specifications
* For a given directory `N-actor-scenes`, all included files represent the same scene (although there are certain limitations, as discussed in our paper).
* For `N=3|N=4`, the scenes are designed for the _town02_ map, where it is expected to be mostly successful (but it might require more than 30 second timeout). For other maps, it is hard to tell if this scene will be successful.
* The `2-actor-scenes/d-sc1.scenic` scene specification is expected to time out due to limitations of _Scenic_.

## CARLA Simulator integration
* Once you have successfully installed the _CARLA_ simulator, you can simulate a scene within the simulator.
* To do so, in the `runScenic.sh` file, uncomment the _Simulator variable definitions
  * The `SIMULATE` variable specifies that you want to see the _CARLA_ simulator, for a specified number of time steps.
  * Generally, the simulator would only include the road network (and no environment elements like houses, or stoplights). However, for certain maps included within _CARLA_ such as _town02_, you may include the environment in the simulation by uncommenting the `CARLAMAP` variable.
  * Additionally, you may want to save images from the point-of-view of the ego vehicle in the simulation. To do so, uncomment and adjust the `IMGDIR` variable.