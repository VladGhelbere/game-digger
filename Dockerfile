FROM ubuntu:latest

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		cron \
		nano \
		python3 \
		python3-pip \
		python3-dev \
		libssl-dev \
		build-essential
		
RUN pip install \
	--upgrade pip \
	pysqlite3 \
	requests \
	discord --no-binary\
	tweepy \
	jsonmerge

RUN mkdir /var/log/game-digger

ADD ./scripts /scripts
ADD ./game-digger.cron /etc/cron.d/game-digger
ADD ./entrypoint.sh /entrypoint.sh

WORKDIR /scripts

ENTRYPOINT ["/entrypoint.sh"]
