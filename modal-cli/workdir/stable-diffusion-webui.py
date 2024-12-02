# This script is made referencing these awesome Japanese websites!
# https://zenn.dev/cp20/articles/stable-diffusion-webui-with-modal
# https://note.com/light_impala137/n/n99b014389a69

from colorama import Fore
from pathlib import Path

import modal
import shutil
import subprocess
import sys
import shlex
import os

# Variables definition related to Modal service
app = modal.App("sd-camenduru-v2.7-app")
vol = modal.Volume.from_name("sd-camenduru-v2.7-vol", create_if_missing=True)

# Paths definition
mount_point = "/workdir"
webui_dir = mount_point + "/stable-diffusion-webui"
webui_model_dir = webui_dir + "/models/Stable-diffusion/"

# Model IDs on Hugging Face
model_ids = [
    {
        "repo_id": "XpucT/Deliberate",
        "model_path": "Deliberate_v2.safetensors",
        "config_file_path": "",
        "model_name": "Deliberate_v2.safetensors",
    },
]


@app.function(
    # For forcing the docker image to rebuild
    # https://modal.com/docs/guide/custom-container#forcing-an-image-to-rebuild
    # image=modal.Image.from_registry("python:3.10.6-slim", force_build=True)
    image=modal.Image.from_registry("python:3.10.6-slim")
    .apt_install(
        "git",
        "libgl1-mesa-dev",
        "libglib2.0-0",
        "libsm6",
        "libxrender1",
        "libxext6",
        "gcc",
        "libcairo2-dev",
        "aria2",
    )
    .run_commands(
        "pip install -e git+https://github.com/CompVis/taming-transformers.git@master#egg=taming-transformers"
    )
    .pip_install(
        "blendmodes==2022",
        "transformers==4.30.2",
        "accelerate==0.21.0",
        "basicsr==1.4.2",
        "gfpgan==1.3.8",
        "gradio==3.41.2",
        "numpy==1.23.5",
        "Pillow==9.5.0",
        "realesrgan==0.3.0",
        "torch",
        "omegaconf==2.2.3",
        "pytorch_lightning==1.9.4",
        "scikit-image==0.21.0",
        "fonts",
        "font-roboto",
        "timm==0.9.2",
        "piexif==1.1.3",
        "einops==0.4.1",
        "jsonmerge==1.8.0",
        "clean-fid==0.1.35",
        "resize-right==0.0.2",
        "torchdiffeq==0.2.3",
        "kornia==0.6.7",
        "lark==1.1.2",
        "inflection==0.5.1",
        "GitPython==3.1.32",
        "torchsde==0.2.6",
        "safetensors==0.3.1",
        "httpcore==0.15",
        "tensorboard==2.9.1",
        "taming-transformers==0.0.1",
        "clip",
        "xformers",
        "test-tube",
        "diffusers",
        "invisible-watermark",
        "pyngrok",
        "xformers==0.0.16rc425",
        "gdown",
        "huggingface_hub",
        "colorama",
        "torchmetrics==0.11.4",
        "fastapi==0.94.0",
        "open-clip-torch==2.20.0",
        "psutil==5.9.5",
        "tomesd==0.1.3",
        "httpx==0.24.1",
    )
    .pip_install(
        "git+https://github.com/mlfoundations/open_clip.git@bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b"
    ),
    secrets=[modal.Secret.from_name("huggingface-secret")],
    volumes={mount_point: vol},
    # Designate the target GPU
    gpu="A10G",
    # gpu=modal.gpu.A10G(count=2),
    # gpu=modal.gpu.T4(count=2),
    timeout=12000,
)

async def run_stable_diffusion_webui():
    print(Fore.CYAN + "\n---------- Start setting up for all models ----------\n")

    webui_dir_path = Path(webui_model_dir)
    if not webui_dir_path.exists():
        # If you encountered RPC failure related error upon git cloning
        # subprocess.run("git config --global http.postBuffer 200M", shell=True)
        subprocess.run(
            f"git clone -b v2.7 https://github.com/camenduru/stable-diffusion-webui {webui_dir}",
            shell=True,
        )

    # Function definition used for downloading files from Hugging face
    def download_hf_file(repo_id, filename):
        from huggingface_hub import hf_hub_download

        download_dir = hf_hub_download(repo_id=repo_id, filename=filename)
        return download_dir

    for model_id in model_ids:
        print(Fore.GREEN + model_id["repo_id"] + " : Start setting up....")

        if not Path(webui_model_dir + model_id["model_name"]).exists():
            # Download and copy for model files
            model_downloaded_dir = download_hf_file(
                model_id["repo_id"],
                model_id["model_path"],
            )
            shutil.copy(
                model_downloaded_dir,
                webui_model_dir + os.path.basename(model_id["model_path"]),
            )

        if "config_file_path" not in model_id:
            continue

        if not Path(webui_model_dir + model_id["config_file_path"]).exists():
            # Download and copy for config files
            config_downloaded_dir = download_hf_file(
                model_id["repo_id"], model_id["config_file_path"]
            )
            shutil.copy(
                config_downloaded_dir,
                webui_model_dir + os.path.basename(model_id["config_file_path"]),
            )

        print(Fore.GREEN + model_id["repo_id"] + " : Finished setting up!")

    print(Fore.CYAN + "\n---------- Finished setting up for all models ----------\n")

    # Activate WebUI
    sys.path.append(webui_dir)
    sys.argv += shlex.split("--skip-install --xformers")
    os.chdir(webui_dir)
    from launch import start, prepare_environment

    prepare_environment()
    # Note that the first argument will be ignored
    sys.argv = shlex.split("--a --gradio-debug --share --xformers --skip-version-check")
    start()


@app.local_entrypoint()
def main():
    run_stable_diffusion_webui.remote()
