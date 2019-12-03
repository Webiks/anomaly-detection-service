#!/bin/bash
eval $(aws ecr get-login --no-include-email --region us-west-2)
docker pull 223455578796.dkr.ecr.us-west-2.amazonaws.com/monitor-anomaly-detection:latest
