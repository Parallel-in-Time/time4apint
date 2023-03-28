#!/bin/bash

for script in *.py
do 
    echo "Executing script $script"
    python $script
done