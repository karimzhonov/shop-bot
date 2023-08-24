FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
RUN apt-get update -y --allow-insecure-repositories
RUN apt-get -y install libev-dev libnss3 gdal-bin libpq5 libgdal-dev python3-gdal binutils libproj-dev

COPY . /app/