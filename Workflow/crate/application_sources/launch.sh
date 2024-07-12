#!/bin/bash -e

  # Define script variables
  scriptDir=$(pwd)/$(dirname $0)
  execFile=${scriptDir}/src/lysozyme_in_water.py
  appPythonpath=${scriptDir}/src/

  # Retrieve arguments
  numNodes=$1
  executionTime=$2
  tracing=$3

  # Leave application args on $@
  shift 3

  # Load necessary modules
  module purge
  module load intel/2017.4 impi/2017.4 mkl/2017.4 bsc/1.0
  export COMPSS_PYTHON_VERSION=3.9.10
  module load COMPSs/3.3
  # Using gmx binary
  export GMX_BIN=/apps/COMPSs/TUTORIALS/Libraries/gromacs5.1.2/bin  # exposes gmx binary
  export PATH=${GMX_BIN}:$PATH
  # Using gmx_mpi binary
  module load gromacs/2016.4                                        # exposes gmx_mpi binary
  # module load intel/2018.4 mkl/2018.4 impi/2018.4 gromacs/2018.3  # exposes gmx_mpi binary
  # Using grace binary
  module load grace/5.1.25
  module load gcc/7.2.0 graphviz

  # Submit the job
  pycompss job submit \
    --provenance \
    --qos=training \
    --num_nodes=${numNodes} \
    --exec_time=${executionTime} \
    --reservation=COMPSs2024 \
    --worker_working_dir=${scriptDir} \
    --tracing=${tracing} \
    --graph=true \
    --log_level=off \
    --pythonpath=${appPythonpath} \
    --lang=python \
    $execFile $@


######################################################
# APPLICATION EXECUTION EXAMPLE
# Call:
#       ./launch.sh <NUMBER_OF_NODES> <EXECUTION_TIME> <TRACING> <CONFIG_PATH> <DATASET_PATH> <OUTPUT_PATH>
#
# Example:
#       ./launch.sh 2 10 true $(pwd)/config/ $(pwd)/dataset/ $(pwd)/output/
#
#####################################################
