#!/bin/bash

# Run the simulator
# HOM: [0, 1,2,3,4,5,6,7,8]
# TTT: [32, 64, 128, 256, 512, 1024]

echo "hom,tty,hopps,hos" > results.csv
for HOM in 0 1 2 3 4 5 6 7 8; do
    for TTT in 32 64 128 256 512 1024; do
        python3 run_simulator.py $HOM $TTT &
    done
done
```