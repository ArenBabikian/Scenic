
KEYPATH='~/.ssh/av-testing-key.pem'

IP='16.171.8.34' #ADJUST
SRCDIR='/home/ubuntu/git/transfuser/issta/res'
DIRNAME='town04-916'
# DIRNAME='town04-916-3-4-colored'
# DIRNAME='town05-2240-3-4'

DIRPATH=$SRCDIR/$DIRNAME
# TGTWS='/c/git/carla/PythonAPI/custom/replay/_logs'
# TGTWS='/c/git/Scenic/issta/sim-data'
TGTWS='/home/aren/git/Scenic/issta/data-sim/Town04_916'
# TGTWS='/home/aren/git/Scenic/issta/data-sim/town05_2240_3_4'
TGTDIR=$TGTWS/'log12'

# SCP from server
cmd_arg="$1"
if [[ "$#" -gt 0 && $cmd_arg == "--scp" ]]; then
    cmd="scp  -r -i $KEYPATH ubuntu@$IP:$DIRPATH $TGTDIR"
    echo $cmd
    eval $cmd
fi

# Then manually rename the folder to /log

exit

# CARLA Must be running on LOCAL
# python Util/Run/runSimulator.py -v 0.9.14?

TGTFULLDIR=$TGTDIR/$DIRNAME
PYTHONFILEPATH='issta/scripts/import_recorder_log.py'
for f in $TGTFULLDIR/*.log; do

    if [ -e "$f" ]; then
    echo "File exists at $f"
    else
    echo "File does not exist at $f"
    fi

    FILENAME=$(basename -s .log $f)
    WSLFILE=$(wslpath -w $f)
    # WSLFILE=$f
    SAVEPATH=${TGTWS}/str2/${FILENAME}.txt
    # cmd="python $PYTHONFILEPATH --savepath $SAVEPATH $f"
    cmd="python $PYTHONFILEPATH '$WSLFILE'"
    echo $cmd
    eval $cmd
    exit
done

exit
