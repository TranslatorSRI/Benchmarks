FROM renciorg/renci-python-image:v0.0.1

ARG VERSION=main


WORKDIR /home/benchmarks

RUN git clone --branch ${VERSION} --single-branch https://github.com/TranslatorSRI/Benchmarks.git

WORKDIR /home/benchmarks/Benchmarks

ENV PYTHONPATH=/home/benchmarks/Benchmarks

RUN pip install --upgrade pip

RUN pip install .

RUN chown nru:nru ./*

USER nru
