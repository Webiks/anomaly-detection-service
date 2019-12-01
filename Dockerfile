# anomaly-detection-app
FROM python:3.8.0-alpine

# set work directory
WORKDIR /user/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MODEL_PATHNAM ./data/model_V0_c0.2.clf

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/app/requirements.txt
RUN pip install -r /usr/app/requirements.txt --user

# TODO: Copy the S2I scripts to /usr/libexec/s2i, since openshift/base-centos7 image
# sets io.openshift.s2i.scripts-url label that way, or update that label
COPY ./s2i/bin/ /usr/app/libexec/s2i

# copy project
COPY . /usr/app/

EXPOSE 56000
CMD [ "python", "anomaly_detection_app.py" ]