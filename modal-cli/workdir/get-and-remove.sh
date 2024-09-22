#!/bin/bash

# Get today's date
today=$(date +%Y-%m-%d)

# Base variables for running commands
nfs_storage_name="stable-diffusion-webui-main"
output_dir="outputs/txt2img-images/${today}"

# Get command
get_command="modal nfs get ${nfs_storage_name} ${output_dir}/*"

# Remove command
rm_command="modal nfs rm -r ${nfs_storage_name} outputs/"

# Run commands
echo "Command for running:"
echo "$get_command"
eval "$get_command"

echo "$rm_command"
eval "$rm_command"
