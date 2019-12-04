#!/bin/bash
eval $(aws ecr get-login --no-include-email --region us-west-2)

APP_VERSION=$(python ./setup.py --version)

docker tag webiks/anomaly-detection-app:$APP_VERSION \
       223455578796.dkr.ecr.us-west-2.amazonaws.com/monitor-anomaly-detection:$APP_VERSION
docker tag webiks/anomaly-detection-app:latest \
       223455578796.dkr.ecr.us-west-2.amazonaws.com/monitor-anomaly-detection:latest

docker push 223455578796.dkr.ecr.us-west-2.amazonaws.com/monitor-anomaly-detection:$APP_VERSION
docker push 223455578796.dkr.ecr.us-west-2.amazonaws.com/monitor-anomaly-detection:latest
