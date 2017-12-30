#!/bin/bash

docker build -t wesparish/eth-value-calculator . && \
  docker push wesparish/eth-value-calculator
