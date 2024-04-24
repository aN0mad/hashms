FROM python:3.11-bullseye

RUN apt update -y
RUN apt install wget\
    git \
    iproute2 \
    build-essential \
    ca-certificates -y && update-ca-certificates

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN echo export PATH="/root/.local/bin:$PATH" >> ~/.bashrc

RUN python3 -m pip install --user pipx
RUN python3 -m pipx ensurepath