FROM python:3.7

WORKDIR /usr/src/app

RUN curl -sSL https://install.python-poetry.org | python - --version 1.5.1 \
    && export PATH="/root/.local/bin:$PATH"
ENV PATH "/root/.local/bin:$PATH"

COPY . .

RUN poetry install

##### CONNECT TO SERVER
# ssh cloud@vm.fured.cloud.bme.hu -p 1627

##### BUILD IMAGE
# sudo docker build -t scenic-ab-official .

##### GENERATE INSTANCES
# sudo docker run -m 16g --name sc-off-ab  -v /home/cloud/catrionam/docker:/usr/src/app/measurements/results scenic-ab-official bash runAllMeasurements.sh 
#
# sudo docker run -m 16g -it --rm --name sc-off-ab -v /home/cloud/arenb/Scenic/docker:/usr/src/app/measurements/results scenic-ab-official bash
# poetry run python src/scenic/runmeasurements.py

##### SIMPLE DOCKER RUNS
# docker run --name oveslantoun -it scenic-ab-official bash

##### WHEN DOCKER IS ALREADY RUNNING
# docker exec -it sc-off-ab bash

##### EXITING
# docker stop sc-off-ab 

##### SCP
# scp -P 18327 -r "cloud@vm.fured.cloud.bme.hu:/home/cloud/arenb/Scenic/measurements/figures/evol/" docker/figures/
# 
# BELOW DOES NOT WORK, OVERWRITES   
# scp -P 18327 -r "cloud@vm.fured.cloud.bme.hu:/home/cloud/arenb/Scenic/docker/zalaFullcrop/*/*/d-nsga/*/_measurementstats.json" docker/
