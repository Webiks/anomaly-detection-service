#!/bin/bash

APP_VERSION=$(python ./setup.py --version)
s2i build ./ centos/python-36-centos7 webiks/anomaly-detection-app:$APP_VERSION
docker tag webiks/anomaly-detection-app:$APP_VERSION webiks/anomaly-detection-app:latest