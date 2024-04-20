# pull official base image
FROM python:3

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
COPY req.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r req.txt

# copy project
COPY . .

EXPOSE 6500