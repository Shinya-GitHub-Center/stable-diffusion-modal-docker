import subprocess

import modal

PORT = 8000

env_app_image = (
    # modal.Image.debian_slim(python_version="3.11", force_build=True)
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "google-perftools",
    )
    .env({"LD_PRELOAD": "/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4"})
    .run_commands(
        "git clone --depth 1 --branch v1.7.0 https://github.com/AUTOMATIC1111/stable-diffusion-webui /webui",
        "python -m venv /webui/venv",
        "cd /webui && . venv/bin/activate && "
        + "python -c 'from modules import launch_utils; launch_utils.prepare_environment()' --xformers",
        gpu="a10g",
    )
    .run_commands(
        "cd /webui && . venv/bin/activate && "
        + "python -c 'from modules import shared_init, initialize; shared_init.initialize(); initialize.initialize()'",
        gpu="a10g",
    )
    .run_commands(
        "rm -rf /webui/models/* && "
        "rm -rf /webui/embeddings/* && "
        "rm -rf /webui/extensions/*"
    )
)

shared_models = modal.Volume.from_name("sd_shared_models", create_if_missing=True)
shared_embeddings = modal.Volume.from_name("sd_shared_embeddings", create_if_missing=True)
shared_extensions = modal.Volume.from_name("sd_shared_extensions", create_if_missing=True)
shared_outputs = modal.Volume.from_name("sd_shared_outputs", create_if_missing=True)

app = modal.App(
    "sd-a1111-v1.7.0-app",
    image=env_app_image,
    volumes={
        "/webui/models": shared_models,
        "/webui/embeddings": shared_embeddings,
        "/webui/extensions": shared_extensions,
        "/webui/outputs": shared_outputs,
    },
)


@app.function(
    gpu="a10g",
    cpu=2,
    memory=1024,
    timeout=12000,
    allow_concurrent_inputs=100,
    keep_warm=1,
)
@modal.web_server(port=PORT, startup_timeout=180)
def run():
    START_COMMAND = f"""
cd /webui && \
. venv/bin/activate && \
accelerate launch \
    --num_processes=1 \
    --num_machines=1 \
    --mixed_precision=fp16 \
    --dynamo_backend=inductor \
    --num_cpu_threads_per_process=6 \
    /webui/launch.py \
        --skip-prepare-environment \
        --no-gradio-queue \
        --listen \
        --port {PORT}
"""
    subprocess.Popen(START_COMMAND, shell=True)
