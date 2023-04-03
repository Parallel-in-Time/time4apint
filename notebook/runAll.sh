#!/bin/bash

for notebook in *.ipynb
do 
    echo "Executing and updating notebook $notebook"
    jupyter nbconvert --execute --to notebook --inplace $notebook
done