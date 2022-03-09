FROM python:3.7

WORKDIR /usr/src/app

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - \
    && export PATH="/root/.local/bin:$PATH"
ENV PATH "/root/.local/bin:$PATH"

COPY . .

RUN poetry install

# ssh cloud@vm.fured.cloud.bme.hu -p 1627

# Build image
# sudo docker build -t scenic .

# Generate the abstract scenes


# Generate the instances
# sudo docker run -m 16g --name scenic-off -v /home/cloud/Scenic/docker:/usr/src/app/measurements/results scenic bash runAllMeasurements.sh 

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