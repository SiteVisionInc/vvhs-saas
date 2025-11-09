#!/bin/bash

# Get current timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Run Git commands
git add .
git commit -m "$timestamp"
git push -u origin main

