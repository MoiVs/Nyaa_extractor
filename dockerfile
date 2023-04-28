FROM python:3.11

WORKDIR /usr/src/app
RUN mkdir -p /usr/src/app/data

RUN pip install NyaaPy lxml

ADD search.py .
ADD parameters.json .

RUN python3 ./search.py