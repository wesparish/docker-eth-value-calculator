FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install python3-pip git python3 vim-tiny curl -y && \
    pip3 install flask requests && \
    apt-get autoremove -y && \
    apt-get clean

ENV LOG_LEVEL="WARN" LC_ALL=C.UTF-8 LANG=C.UTF-8

COPY eth-value-calculator.py /eth-value-calculator.py
RUN chown root:root eth-value-calculator.py

ENTRYPOINT ["/eth-value-calculator.py"]
