FROM ubuntu:latest

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		cron \
		nano \
		python3 \
		python3-pip \
		python3-dev \
		python3-tweepy \
		libssl-dev \
		build-essential \
		libpq-dev
		
RUN pip install \
	psycopg2 \
	requests \
	jsonmerge \
	discord --no-binary \
	tweepy

RUN mkdir /var/log/game-digger

ADD ./scripts /scripts
ADD ./game-digger.cron /etc/cron.d/game-digger
ADD ./entrypoint.sh /entrypoint.sh

WORKDIR /scripts

ENTRYPOINT ["/entrypoint.sh"]
