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

### For model files one by one
Put any model files (including base and refiner models) into your local `Stable-diffusion` directory and execute the following command to proceed uploading

`@workdir`
```
modal volume put sd_shared_models models/Stable-diffusion/<model_file_name> /Stable-diffusion/
```
### For whole model directory at once  (suitable for the first time of the whole directory uploading)
Warning! : this procedure will be failed if the same model (file) names are already located on the modal server (not overwrite the whole model directory though...)

`@workdir`
```
modal volume put sd_shared_models models/Stable-diffusion/ /Stable-diffusion/
```

### For Lora files one by one
Put any Lora files into your local `Lora` directory and execute the following command to proceed uploading

`@workdir`
```
modal volume put sd_shared_models models/Lora/<lora_file_name> /Lora/
```

### For whole Lora directory at once  (suitable for the first time of the whole directory uploading)
Warning! : this procedure will be failed if the same lora (file) names are already located on the modal server (not overwrite the whole lora directory though...)

`@workdir`
```
modal volume put sd_shared_models models/Lora/ /Lora/
```

### For VAE files one by one
Put any VAE files into your local `VAE` directory and execute the following command to proceed uploading

`@workdir`
```
modal volume put sd_shared_models models/VAE/<vae_file_name> /VAE/
```

### For whole VAE directory at once  (suitable for the first time of the whole directory uploading)
Warning! : this procedure will be failed if the same VAE (file) names are already located on the modal server (not overwrite the whole VAE directory though...)

`@workdir`
```
modal volume put sd_shared_models models/VAE/ /VAE/
```

### For embedding files one by one
Put any embedding files into your local `embeddings` directory and execute the following command to proceed uploading

`@workdir`
```
modal volume put sd_shared_embeddings embeddings/<embedding_file_name> /
```

## Etc...
### As for forcing the docker image on modal server to rebuild
If you want to rebuild docker image on modal server, such as for updating to the latest modules or packages

`webui.py`
```
modal.Image.debian_slim(python_version="3.11", force_build=True)
```

### How to designate your workspace environment upon executing any modal commands
If you have multiple environment for your workspace on modal, you may need to add `-e<your_env_name>` option for all modal commands. (You can ignore this if you have already set your favored environment via `.modal.toml`)

### How to make `style.css` persistent
Please install [Styles-Editor extension](https://github.com/chrisgoringe/Styles-Editor.git) and set your prompts into this extension's tab. (Data will be auto-saved in every 10 mins)  
If you want to restore data, please select the latest date-and-time csv file from dropdown menu then click restore from Styles-Editor tab.

## Reference URL
[Official modal example](https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/stable_diffusion/a1111_webui.py)
