#!/bin/bash

# Get today's date
today=$(date +%Y-%m-%d)

# Base variables for running commands
volume_name="sd_shared_outputs"
output_dir="/txt2img-images/${today}"
local_output_dir="./outputs"

# Get command
get_command="modal volume get ${volume_name} ${output_dir}/ ${local_output_dir}"

# Remove command
rm_command="modal volume rm -r ${volume_name} /txt2img-grids/${today} && \
    modal volume rm -r ${volume_name} /txt2img-images/${today}"

# Run commands
echo "Command for running:"
echo "$get_command"
eval "$get_command"

echo "$rm_command"
eval "$rm_command"
