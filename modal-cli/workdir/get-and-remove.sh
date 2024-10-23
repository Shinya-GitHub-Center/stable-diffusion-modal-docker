#!/bin/bash

# Get today's date
today=$(date +%Y-%m-%d)

# Base variables for running commands
volume_name="sd-camenduru-v2.7-vol"
output_dir="/stable-diffusion-webui/outputs/txt2img-images/${today}"
local_output_dir="./outputs"

# Get command
get_command="modal volume get ${volume_name} ${output_dir}/ ${local_output_dir}"

# Remove command
rm_command="modal volume rm -r ${volume_name} /stable-diffusion-webui/outputs/"

# Run commands
echo "Command for running:"
echo "$get_command"
eval "$get_command"

echo "$rm_command"
eval "$rm_command"
