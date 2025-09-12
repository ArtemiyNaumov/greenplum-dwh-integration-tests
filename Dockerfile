FROM python:3.7-slim-stretch

WORKDIR /usr/app

COPY . .

RUN mkdir -p check_results

RUN python3.7 -m pip install --upgrade pip && \
  python3.7 setup.py install && \
  rm -rf \
    /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
    /usr/share/man \
    /usr/share/doc \
    /usr/share/doc-base \
    ~/.cache/pip
