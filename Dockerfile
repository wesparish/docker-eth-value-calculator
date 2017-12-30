FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install python3-pip git python3 vim-tiny curl -y && \
    pip3 install requests && \
    git clone https://github.com/corpetty/py-etherscan-api.git /py-etherscan-api && \
    cd /py-etherscan-api && \
    python3 setup.py install && \
    cd / && \
    apt-get autoremove -y && \
    apt-get clean

ENV LOG_LEVEL="WARN" 

COPY eth-value-calculator.py /eth-value-calculator.py
RUN chown root:root eth-value-calculator.py

ENTRYPOINT ["/eth-value-calculator.py"]
