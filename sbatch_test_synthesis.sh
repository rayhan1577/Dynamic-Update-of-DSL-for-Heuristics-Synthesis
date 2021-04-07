#!/bin/bash

for map_index in {1..3}; do
	for trials in {1..2}; do
		echo ${map_index}
		echo ${trials}
	
		sbatch --export=map_index="${map_index}",trials=${trials} run_synthesis.sh
	done
done
