FROM ubuntu:16.04

WORKDIR /usr/home

RUN \
	apt-get update && \
	apt-get install -y python3 python3-pip git && \
	git clone https://github.com/dshepelev15/service_data_handler.git && \
	mv /usr/home/service_data_handler/service.py /usr/home/service.py && \
	mv /usr/home/service_data_handler/data_handler.py /usr/home/data_handler.py && \
	mv /usr/home/service_data_handler/requirements.txt /usr/home/requirements.txt && \
	pip3 install -r requirements.txt

CMD ["python3", "service.py"]