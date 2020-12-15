FROM alpine:3.11
RUN apk update && apk upgrade && \
    apk add --no-cache git less vim curl man diffutils python3 py3-yaml bash openssh docker-cli && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

RUN curl https://storage.googleapis.com/kpt-dev/latest/linux_amd64/kpt -o /usr/local/bin/kpt
RUN chmod +x /usr/local/bin/kpt

COPY e2e/ /e2e/

ENTRYPOINT ["python3", "/e2e/run.py"]