# Getting started with this repo
Use the scene specification files in this folder to get started with this repo.

## How to run the scene specification files
* The best way to get started with this repo is to run the `runScenic.sh` file located _in this directory_ by using the command `bash examplesResearch/basic/runScenic.sh` while in the root directory.
* `runScenic.sh` contains a few customizable variables such as `MAPNAME`, `PATHTOCONFIGFILE` and `USEMHS`:
  * You can change the `PATHTOCONFIGFILE` variable to point to the scene you want to run
  * The `USEMHS` variable specifies whether you want to use vanilla _Scenic_ (`USEMHS=False`), or whether you want to use the novel _MetaHeuristric Search (MHS)_ approach implemented in this repo (`USEMHS=True`). 
  * __NOTE 1:__ when `USEMHS=True`, make sure you are running a mhs-compatible scene specification. mhs-compatible means that the file name contains "mhs" (this is a coincidence for this directory, it is not checked by the program).
  * __NOTE 2:__ when `USEMHS` is enabled, the program considers the constraints specified within the `param constraints` variable of the scene specification file. Otherwise, the variable value is ignored, and the remainder of the document is considered. This is not entirely true, but it is true enough to get started.
  * __NOTE 3:__ The specific configuration of _MHS_ to be used is defined by the `evol-algo` and `evol-opt` command line arguments, which represent the specific _MHS_ algorithm to use (default : _NSGA2_) and the objective function aggregation strategy (default : actor-based aggregation), respectively. Various other configurations exist, but are not necessarily relevant at this stage.
  * You can also play around with some of the other command line arguments, but this may not be very relevant.

## A note about certain command-line arguments
* `--count N` : this specifies the total number of concrete scenes (solutions) we will end up with. So we will run the program in a loop until we generate `N` solutions.
* `-p evol-NumSols M` : this specifies the maximum number of solutions that can be saved when running a single MHS process.

### Example 1
Let's say the MHS process yield a set `S` of `X` solutions. Solutions are either all approximate, or all non-approximate.

As such, for a given MHS process, the program will save `min(M, X)` solutions, since
1. We don't want to save more than `M` solutions, and
2. More than `X` solutions are not available.

The general trend is as follows:
* If `S` contains non-approximate solutions, then usually `X<M` (`X` is often either 1 or 2).
* If `S` contains approximate solutions (i.e. if no full solution is found), then usually `X>M` (`X` is closer to the population size).

Note that if `M=-1`, then all solutions in `S` will be saved.

### Example 2
For instance, in the case where `N=10` and `M=3`, we will continuously run MHS processes (and store at most 3 solutions after each run) until we have stored a total of 10 solutions.

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