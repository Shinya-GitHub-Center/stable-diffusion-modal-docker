# If your logging-in user at host has a different User / Group ID,
# please change the both value for UID & GID `1000`
# to your desired ID number.

FROM python:3.11
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
