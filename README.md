# stable-diffusion-modal-docker
How to deploy Stable Diffusion via Docker container using modal client

![logotype-bb8cd083](https://github.com/Shinya-GitHub-Center/stable-diffusion-modal-docker/assets/129726604/071b609b-7ba7-4435-8da4-f22b5fa99791)
![horizontal-logo-monochromatic-white](https://github.com/Shinya-GitHub-Center/stable-diffusion-modal-docker/assets/129726604/7fcbb3c4-e62d-408b-b49b-fc4f9702952a)

## About
I recommend using python docker container instead of using venv, since `download-output.py` does not work properly if the host machine's python version is 3.8 (default version of ubuntu20.04)

## Create a Modal API Token designated only for use for this docker container project
modal.com => LOG IN => SETTINGS => New Token => copy the command showed up below => close the window  
(Do not lose the copied command, this will be required later...)

## Copy the huggingface API Token value @ huggingface
huggingface.co => Log In => settings => Access Tokens => New token => copy it

## Paste the huggingface Token to modal's secret
modal.com => LOG IN => SECRETS => Create new secret => Hugging Face => Paste the value (key : HUGGINGFACE_TOKEN) => next => set the secret name to "my-huggingface-secret" => create

## Create this directory into your local machine (I named the root directory name `stable-diffusion-modal-docker`)

```bash
.
├── docker/
│   └── modal-cli/
│       └── Dockerfile
├── docker-compose.yml
└── modal-cli/
    ├── .modal.toml
    └── workdir/
        ├── download-output.py
        ├── models/
        │   ├── Lora/
        │   ├── Stable-diffusion/
        │   └── VAE/
        ├── outputs/
        │   ├── txt2img-grids/
        │   └── txt2img-images/
        └── stable-diffusion-webui.py
```

## Code for `.modal.toml`
```
[default]
token_id = "aa-aaaaaa"
token_secret = "bb-bbbbbb"
```
Please replace `aa-aaaaaa` and `bb-bbbbbb` with your previously copied modal token id and secret  
(modal token set --token-id **aa-aaaaaa** --token-secret **bb-bbbbbb**)

Please make sure any spaces is not included at the end of both id and secret

## Code for `Dockerfile`
```
# If your logging-in user at host has a different User / Group ID,
# please change the both value for UID & GID `1000`
# to your desired ID number.

FROM python:3.10.6
ARG USERNAME=sd-webui
ARG GROUPNAME=sd-webui
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID $USERNAME
WORKDIR /home/sd-webui
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y vim less tree jq
RUN pip install modal colorama pathlib
WORKDIR /home/sd-webui/workdir
```

## Code for `docker-compose.yml`
```
# If you want to use the original `.modal.toml` file,
# located at your host machine's user home directory,
# please replace `source: ./modal-cli/.modal.toml`
# with `source: ~/.modal.toml`

version: "3.8"
services:
  modal-cli:
    build:
      context: ./docker/modal-cli
      dockerfile: Dockerfile
    volumes:
      - type: bind
        source: ./modal-cli/workdir
        target: /home/sd-webui/workdir
      - type: bind
        source: ./modal-cli/.modal.toml
        target: /home/sd-webui/.modal.toml
    user: sd-webui
    tty: true
    stdin_open: true
```

## Code for `stable-diffusion-webui.py`
```
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
stub = modal.Stub("stable-diffusion-webui")
volume_main = modal.NetworkFileSystem.new().persisted("stable-diffusion-webui-main")

# Paths definition
webui_dir = "/content/stable-diffusion-webui"
webui_model_dir = webui_dir + "/models/Stable-diffusion/"

# Model IDs on Hugging Face
model_ids = [
    {
        "repo_id": "XpucT/Deliberate",
        "model_path": "Deliberate_v2.safetensors",
        "config_file_path": "",
        "model_name": "Deliberate_v2.safetensors",
    },
    {
        "repo_id": "WarriorMama777/OrangeMixs",
        "model_path": "Models/BloodOrangeMix/BloodNightOrangeMix.ckpt",
        "config_file_path": "",
        "model_name": "BloodNightOrangeMix.ckpt",
    },
]


@stub.function(
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
        "torchsde==0.2.5",
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
    secret=modal.Secret.from_name("my-huggingface-secret"),
    network_file_systems={webui_dir: volume_main},
    # Designate the target GPU
    gpu="A10G",
    # gpu=modal.gpu.A10G(count=2),
    # gpu=modal.gpu.T4(count=2),
    timeout=12000,
)
async def run_stable_diffusion_webui(): 
    subprocess.run("git config --global http.postBuffer 200M", shell=True)
    print(Fore.CYAN + "\n---------- Start setting up for all models ----------\n")

    webui_dir_path = Path(webui_model_dir)
    if not webui_dir_path.exists():
        subprocess.run(
            f"git clone -b v2.6 https://github.com/camenduru/stable-diffusion-webui {webui_dir}",
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


@stub.local_entrypoint()
def main():
    run_stable_diffusion_webui.remote()
```

## Code for `download-output.py`
```
# This script is made referencing these awesome Japanese websites!
# https://zenn.dev/cp20/articles/stable-diffusion-webui-with-modal

import os
import modal
import subprocess
from concurrent import futures

stub = modal.Stub("stable-diffusion-webui-download-output")

volume_key = "stable-diffusion-webui-main"
volume = modal.NetworkFileSystem.new().persisted(volume_key)

webui_dir = "/content/stable-diffusion-webui/"
remote_outputs_dir = "outputs"
output_dir = "./outputs"


@stub.function(
    network_file_systems={webui_dir: volume},
)
def list_output_image_path(cache: list[str]):
    absolute_remote_outputs_dir = os.path.join(webui_dir, remote_outputs_dir)
    image_path_list = []
    for root, dirs, files in os.walk(top=absolute_remote_outputs_dir):
        for file in files:
            if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            absolutefilePath = os.path.join(root, file)
            relativeFilePath = absolutefilePath[(len(absolute_remote_outputs_dir)) :]
            if not relativeFilePath in cache:
                image_path_list.append(relativeFilePath.lstrip("/"))
    return image_path_list


def download_image_using_modal(image_path: str):
    download_dest = os.path.dirname(os.path.join(output_dir, image_path))
    os.makedirs(download_dest, exist_ok=True)
    subprocess.run(
        f"modal nfs get {volume_key} {os.path.join(remote_outputs_dir, image_path)} {download_dest}",
        shell=True,
    )


@stub.local_entrypoint()
def main():
    cache = []

    for root, dirs, files in os.walk(top=output_dir):
        for file in files:
            relativeFilePath = os.path.join(root, file)[len(output_dir) :]
            cache.append(relativeFilePath)

    image_path_list = list_output_image_path.remote(cache)

    print(f"\nTotal of {len(image_path_list)} files are now being downloaded....\n")

    future_list = []
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        for image_path in image_path_list:
            future = executor.submit(download_image_using_modal, image_path=image_path)
            future_list.append(future)
        _ = futures.as_completed(fs=future_list)

    print(f"\nDownload completed!\n")
```

## How to deploy docker container
@project's root directory
```
docker compose up -d
docker exec -it <container name> bash
modal run stable-diffusion-webui.py
```

## How to download generated pictures into your local machine
```
modal run download-output.py
```

## As for LoRA file addition
Put the LoRA files into Lora directory and execute the following command
```
modal nfs put stable-diffusion-webui-main models/Lora/<lora file name> models/Lora/
```
Alternatively, you can upload whole directory into Modal server - for multiple LoRA files at a time  
(this procedure will overwrite the previously located any Lora files)
```
modal nfs put stable-diffusion-webui-main models/Lora/ models/Lora/
```

## As for VAE file addition
Put the VAE files into VAE directory and execute the following command
```
modal nfs put stable-diffusion-webui-main models/VAE/<vae file name> models/VAE/
```
Alternatively, you can upload whole directory into Modal server - for multiple VAE files at a time  
(this procedure will overwrite the previously located any VAE files)
```
modal nfs put stable-diffusion-webui-main models/VAE/ models/VAE/
```

## As for adding models manually
Put any model files (including base and refiner models) into Stable-diffusion directory and execute the following command
```
modal nfs put stable-diffusion-webui-main models/Stable-diffusion/<model file name> models/Stable-diffusion/
```
or, whole directory at once  
(this procedure will overwrite the previously located any models)
```
modal nfs put stable-diffusion-webui-main models/Stable-diffusion/ models/Stable-diffusion/
```

## As for deleting outputs folder on Modal server
Sometimes upon executing `download-output.py`, the previously downloaded files are downloaded again, to prevent this, please execute the following command prior to creating any new pictures with stable diffusion webui
```
modal nfs rm -r stable-diffusion-webui-main outputs/
```

## As for forcing the docker image to rebuild
If you want to rebuild docker image, such as for updating to the latest modules or packages, please refer to [here](https://modal.com/docs/guide/custom-container#forcing-an-image-to-rebuild)

`stable-diffusion-webui.py`
```
image=modal.Image.from_registry("python:3.10.6-slim", force_build=True)
```

## Reference URL
https://qiita.com/fkgw/items/eaa431b974af20b57179  
https://zenn.dev/cp20/articles/stable-diffusion-webui-with-modal  
https://note.com/light_impala137/n/n99b014389a69
