
FROM python:3.9-slim-bullseye AS base 

ARG APP_DIR=/usr/app/

USER root

RUN mkdir ${APP_DIR}

WORKDIR ${APP_DIR}

RUN pip install -U pip

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git


ENV CONDA_DIR /opt/conda
RUN apt install wget
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_23.11.0-2-Linux-x86_64.sh -O ~/miniconda.sh && \
/bin/bash ~/miniconda.sh -b -p /opt/conda

ENV PATH=$CONDA_DIR/bin:$PATH
RUN conda install -c conda-forge scikit-surprise -y
RUN git clone https://github.com/gdmarmerola/cfml_tools.git
WORKDIR ${APP_DIR}/cfml_tools
RUN python setup.py install
WORKDIR ${APP_DIR}

WORKDIR ${APP_DIR}
COPY requirements.txt ${APP_DIR}

RUN pip install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt
RUN chmod +x /usr/share/tesseract-ocr
RUN su -
RUN apt-get install sudo
CMD ["python3", "src/main.py"]

