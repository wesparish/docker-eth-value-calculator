FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install python3-pip git python3 vim-tiny curl -y && \
    pip3 install python-dateutil flask requests XlsxWriter && \
    apt-get autoremove -y && \
    apt-get clean

ENV LOG_LEVEL="WARN" LC_ALL=C.UTF-8 LANG=C.UTF-8

ADD static /static
ADD templates /templates
COPY eth-value-calculator.py /eth-value-calculator.py
RUN chown root:root eth-value-calculator.py

EXPOSE 5000

ENTRYPOINT ["/eth-value-calculator.py"]
CMD ["-s"]
