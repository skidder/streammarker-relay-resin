FROM resin/raspberrypi2-python:3.5-wheezy

ENV INITSYSTEM on

RUN pip2 install pyserial
RUN pip3 install xbee

ADD streammarker-relay.py /

CMD ["python","/streammarker-relay.py"]
