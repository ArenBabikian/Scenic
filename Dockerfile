FROM python:3.7

WORKDIR /usr/src/app

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - \
    && export PATH="/root/.local/bin:$PATH"
ENV PATH "/root/.local/bin:$PATH"

COPY . .

RUN poetry install

# ssh cloud@vm.fured.cloud.bme.hu -p 1627

# Build image
# sudo docker build -t scenic-ab-official .

# Generate the abstract scenes


# Generate the instances
# sudo docker run -m 16g --name sc-off-ab  -v /home/cloud/catrionam/docker:/usr/src/app/measurements/results scenic bash runAllMeasurements.sh 
# sudo docker run -m 16g -it --rm --name sc-off-ab -v /home/cloud/arenb/Scenic/docker:/usr/src/app/measurements/results scenic-ab-official bash
# poetry run python src/scenic/runmeasurements.py

# docker run --name oveslantoun -it abc1 bash
# # for cmd line
# or
# docker create --name oveslantoun -it abc1

# # When exited
# docker start oveslantoun

# docker stop oveslantoun

# # when runing
# docker exec -it oveslantoun bash

# exit in bash
# or
# docker stop oveslantoun