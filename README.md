# stable-diffusion-modal-docker
How to deploy Stable Diffusion via Docker container using modal client

![logotype-bb8cd083](https://github.com/Shinya-GitHub-Center/stable-diffusion-modal-docker/assets/129726604/071b609b-7ba7-4435-8da4-f22b5fa99791)
![horizontal-logo-monochromatic-white](https://github.com/Shinya-GitHub-Center/stable-diffusion-modal-docker/assets/129726604/7fcbb3c4-e62d-408b-b49b-fc4f9702952a)

## [Go to previously released 'camenduru version'](https://github.com/Shinya-GitHub-Center/stable-diffusion-modal-docker/tree/camenduru-ver)

## Feature
- All debian packages and python libraries (using venv) are stored at remote env image.
- The webui app is stored inside the env image directory, but `models/`, `embeddings/`. `extensions/`, and `outputs/` directories are mounted to the external volumes separately so that you can share those directores with different apps later.
- `modal serve (deploy)` style, the base code was sourced from the official sample.


## Pros
1. You can match the version of python both for your local env and modal server.
2. You can use a modal API Token, which can be used and occupied only for this docker container. (You can also set your working environment on modal workspace to use)
3. You can store Models, embeddings, extensions, and generated pics forever into external (eternal) volume on modal server, simultaneously you can share those volumes between diffrent apps deployed onto your modal workspace!

## Create a Modal API Token designated only for use for this docker container project
modal.com => LOG IN => SETTINGS => New Token => copy the command showed up below => close the window  
(Do not lose the copied command, this will be required later...)

## Code for `.modal.toml`
```
[default]
token_id = "aa-aaaaaa"
token_secret = "bb-bbbbbb"
# environment = "working_env_name"
```
Please replace `aa-aaaaaa` and `bb-bbbbbb` with your previously copied modal token id and secret  
(modal token set --token-id **aa-aaaaaa** --token-secret **bb-bbbbbb**)  
You can also set the modal server's working environment for this project to work (skippable)

Please make sure any spaces is not included at the end of both id and secret

## How to deploy docker container
@project's root directory
```
docker compose up -d
docker exec -it <container name> bash
modal serve webui.py
```
or for the last code
```
modal deploy webui.py
```

## How to download generated pictures into your local machine
Please run the command `bash ./get-and-remove.sh`  
(This command will download all your created pics today to the local machine, then delete those of all pics at the modal server)

## How to manually upload locally stored models, Lora, VAE, and embeddings files

Of course, under construction

## As for forcing the docker image on modal server to rebuild
If you want to rebuild docker image on modal server, such as for updating to the latest modules or packages

`webui.py`
```
modal.Image.debian_slim(python_version="3.11", force_build=True)
```

## Reference URL
[Official modal example](https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/stable_diffusion/a1111_webui.py)
