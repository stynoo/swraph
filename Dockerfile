FROM alpine:3.18.3

LABEL description="SWRAPH : a dockerized weatherdata to mqtt implementation"
LABEL maintainer="Stynoo"

ENV PROJECT=swraph
ENV PROJECT_DIR=/home/$PROJECT

WORKDIR $PROJECT_DIR

# Run `docker build --no-cache .` to update dependencies
RUN apk update --no-cache \
    && apk add --no-cache python3 su-exec \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip paho-mqtt \
    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
    && rm -r /root/.cache

COPY swraph.py /home/swraph/swraph.py

RUN adduser -D -g '' $PROJECT \
    && chown -R $PROJECT:$PROJECT $PROJECT_DIR \
    && chmod a+x /home/swraph/swraph.py

CMD ["/sbin/su-exec", "swraph", "/usr/bin/python3", "/home/swraph/swraph.py"]
