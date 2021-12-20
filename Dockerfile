FROM python:3.7

WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# RUN pip install scenic
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - \
    && export PATH="/root/.local/bin:$PATH" \
    && poetry install \
    && poetry run scenic --help
ENV PATH "/root/.local/bin:$PATH"
# RUN ls /root/.local/bin
# RUN echo $PATH
# RUN 
# RUN echo $PATH
# RUN poetry --version

# ssh cloud@vm.fured.cloud.bme.hu -p 1627

# docker build -t abc1 .

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