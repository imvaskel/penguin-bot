#!/bin/bash

# Run
docker run -d \
--rm \
--name=penguin-bot \
--restart always \
penguin-bot:latest