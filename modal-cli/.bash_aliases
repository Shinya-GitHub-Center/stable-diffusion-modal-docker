# Aliases and functions scoping only for 'stable-diffusion-modal-docker' container
# Aliases
alias serve='modal serve webui.py'
alias deploy='modal deploy webui.py'

# Functions required with one parameter
putmodel() {
    command modal volume put sd_shared_models /home/sd-webui/workdir/models/Stable-diffusion/"$1" /Stable-diffusion/
}

putdirmodel() {
    command modal volume put sd_shared_models /home/sd-webui/workdir/models/Stable-diffusion/ /Stable-diffusion/
}

putlora() {
    command modal volume put sd_shared_models /home/sd-webui/workdir/models/Lora/"$1" /Lora/
}

putdirlora() {
    command modal volume put sd_shared_models /home/sd-webui/workdir/models/Lora/ /Lora/
}

putvae() {
    command modal volume put sd_shared_models /home/sd-webui/workdir/models/VAE/"$1" /VAE/
}

putdirvae() {
    command modal volume put sd_shared_models /home/sd-webui/workdir/models/VAE/ /VAE/
}

putembedding() {
    command modal volume put sd_shared_embeddings /home/sd-webui/workdir/embeddings/"$1" /
}
