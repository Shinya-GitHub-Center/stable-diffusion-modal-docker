# stable-diffusion-modal-docker
How to deploy Stable Diffusion via Docker container using modal client

## About
I recommend using python docker container instead of using venv, since "download-output.py" did not work properly if the host machine's python version was 3.8 (default version of ubuntu20.04)

## Preparing
Prior to proceeding this project, you need to generate `.modal.toml` to your local machine's user home directory.  
This can be done with proceeding [this](https://zenn.dev/cp20/articles/stable-diffusion-webui-with-modal#2.-modal%E3%82%92%E5%8B%95%E3%81%8B%E3%81%97%E3%81%A6%E3%81%BF%E3%82%8B) using venv. (seems like token file will be generated into host machine's home directory)

## Create this directory into your local machine (I chose the root directory name for "stable-diffusion-modal-docker")

```bash
.
├── docker
│   └── modal-cli
│       └── Dockerfile
├── docker-compose.yml
└── modal-cli
    └── workdir
        ├── download-output.py
        ├── models
        │   ├── Lora
        │   └── Stable-diffusion
        ├── outputs
        │   ├── txt2img-grids
        │   └── txt2img-images
        └── stable-diffusion-webui.py
```

## Code for `Dockerfile`
```
FROM python:latest
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
RUN pip install modal-client colorama pathlib
WORKDIR /home/sd-webui/workdir
```

## Code for `docker-compose.yml`
```
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
        source: ~/.modal.toml
        target: /home/sd-webui/.modal.toml
    user: sd-webui
    tty: true
    stdin_open: true
```

## Code for `stable-diffusion-webui.py`
```
from colorama import Fore
from pathlib import Path

import modal
import shutil
import subprocess
import sys
import shlex
import os

# modal系の変数の定義
stub = modal.Stub("stable-diffusion-webui")
volume_main = modal.SharedVolume().persist("stable-diffusion-webui-main")

# 色んなパスの定義
webui_dir = "/content/stable-diffusion-webui"
webui_model_dir = webui_dir + "/models/Stable-diffusion/"

# モデルのID
model_ids = [
    {
        "repo_id": "XpucT/Deliberate",
        "model_path": "Deliberate_v2.safetensors",
        "config_file_path": "",
    },
    {
        "repo_id": "sazyou-roukaku/chilled_remix",
        "model_path": "chilled_remix_v1vae.safetensors",
        "config_file_path": "",
    },
    {
        "repo_id": "Lykon/NeverEnding-Dream",
        "model_path": "NeverEndingDream_ft_mse.safetensors",
        "config_file_path": "",
    },
]


@stub.function(
    image=modal.Image.from_dockerhub("python:3.8-slim")
    .apt_install(
        "git", "libgl1-mesa-dev", "libglib2.0-0", "libsm6", "libxrender1", "libxext6"
    )
    .run_commands(
        "pip install -e git+https://github.com/CompVis/taming-transformers.git@master#egg=taming-transformers"
    )
    .pip_install(
        "blendmodes==2022",
        "transformers==4.25.1",
        "accelerate==0.12.0",
        "basicsr==1.4.2",
        "gfpgan==1.3.8",
        "gradio==3.16.2",
        "numpy==1.23.3",
        "Pillow==9.4.0",
        "realesrgan==0.3.0",
        "torch",
        "omegaconf==2.2.3",
        "pytorch_lightning==1.7.6",
        "scikit-image==0.19.2",
        "fonts",
        "font-roboto",
        "timm==0.6.7",
        "piexif==1.1.3",
        "einops==0.4.1",
        "jsonmerge==1.8.0",
        "clean-fid==0.1.29",
        "resize-right==0.0.2",
        "torchdiffeq==0.2.3",
        "kornia==0.6.7",
        "lark==1.1.2",
        "inflection==0.5.1",
        "GitPython==3.1.27",
        "torchsde==0.2.5",
        "safetensors==0.2.7",
        "httpcore<=0.15",
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
    )
    .pip_install("git+https://github.com/mlfoundations/open_clip.git@bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b"),
    secret=modal.Secret.from_name("my-huggingface-secret"),
    shared_volumes={webui_dir: volume_main},
    gpu="T4",
    timeout=6000,
)
async def run_stable_diffusion_webui():
    print(Fore.CYAN + "\n---------- セットアップ開始 ----------\n")

    webui_dir_path = Path(webui_model_dir)
    if not webui_dir_path.exists():
        subprocess.run(f"git clone -b v2.2 https://github.com/camenduru/stable-diffusion-webui {webui_dir}", shell=True)

    # Hugging faceからファイルをダウンロードしてくる関数
    def download_hf_file(repo_id, filename):
        from huggingface_hub import hf_hub_download

        download_dir = hf_hub_download(repo_id=repo_id, filename=filename)
        return download_dir


    for model_id in model_ids:
        print(Fore.GREEN + model_id["repo_id"] + "のセットアップを開始します...")

        if not Path(webui_model_dir + model_id["model_path"]).exists():
            # モデルのダウンロード＆コピー
            model_downloaded_dir = download_hf_file(
                model_id["repo_id"],
                model_id["model_path"],
            )
            shutil.copy(model_downloaded_dir, webui_model_dir + model_id["model_path"])

        if "config_file_path" not in model_id:
          continue

        if not Path(webui_model_dir + model_id["config_file_path"]).exists():
            # コンフィグのダウンロード＆コピー
            config_downloaded_dir = download_hf_file(
                model_id["repo_id"], model_id["config_file_path"]
            )
            shutil.copy(
                config_downloaded_dir, webui_model_dir + model_id["config_file_path"]
            )

        print(Fore.GREEN + model_id["repo_id"] + "のセットアップが完了しました！")

    print(Fore.CYAN + "\n---------- セットアップ完了 ----------\n")

    # WebUIを起動
    sys.path.append(webui_dir)
    sys.argv += shlex.split("--skip-install --xformers")
    os.chdir(webui_dir)
    from launch import start, prepare_environment

    prepare_environment()
    # 最初のargumentは無視されるので注意
    sys.argv = shlex.split("--a --gradio-debug --share --xformers")
    start()


@stub.local_entrypoint
def main():
    run_stable_diffusion_webui.call()
```

## Code for `download-output.py`
```
import os
import modal
import subprocess
from concurrent import futures

stub = modal.Stub("stable-diffusion-webui-download-output")

volume_key = 'stable-diffusion-webui-main'
volume = modal.SharedVolume().persist(volume_key)

webui_dir = "/content/stable-diffusion-webui/"
remote_outputs_dir = 'outputs'
output_dir = "./outputs"


@stub.function(
    shared_volumes={webui_dir: volume},
)
def list_output_image_path(cache: list[str]):
  absolute_remote_outputs_dir = os.path.join(webui_dir, remote_outputs_dir)
  image_path_list = []
  for root, dirs, files in os.walk(top=absolute_remote_outputs_dir):
    for file in files:
      if not file.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

      absolutefilePath = os.path.join(root, file)
      relativeFilePath = absolutefilePath[(len(absolute_remote_outputs_dir)) :]
      if not relativeFilePath in cache:
        image_path_list.append(relativeFilePath.lstrip('/'))
  return image_path_list

def download_image_using_modal(image_path: str):
  download_dest = os.path.dirname(os.path.join(output_dir, image_path))
  os.makedirs(download_dest, exist_ok=True)
  subprocess.run(f'modal volume get {volume_key} {os.path.join(remote_outputs_dir, image_path)} {download_dest}', shell=True)

@stub.local_entrypoint
def main():
  cache = []

  for root, dirs, files in os.walk(top=output_dir):
    for file in files:
      relativeFilePath = os.path.join(root, file)[len(output_dir) :]
      cache.append(relativeFilePath)

  image_path_list = list_output_image_path.call(cache)

  print(f'\n{len(image_path_list)}ファイルのダウンロードを行います\n')

  future_list = []
  with futures.ThreadPoolExecutor(max_workers=10) as executor:
    for image_path in image_path_list:
        future = executor.submit(download_image_using_modal, image_path=image_path)
        future_list.append(future)
    _ = futures.as_completed(fs=future_list)

  print(f'\nダウンロードが完了しました\n')
```
## As for LoRA file addition
Put the LoRA files into Lora directory and execute the following command
```
modal volume put stable-diffusion-webui-main models/Lora/<lora file name> models/Lora/
```

## As for deleting outputs folder on Modal server
Sometimes upon executing `download-output.py`, the previously downloaded files are downloaded again, to prevent this, please execute the following command prior to creating any new pictures with stable diffusion webui
```
modal volume rm -r stable-diffusion-webui-main outputs/
```

## Reference URL
https://zenn.dev/cp20/articles/stable-diffusion-webui-with-modal