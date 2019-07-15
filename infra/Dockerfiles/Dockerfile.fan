FROM alpine:latest

LABEL name "Alan Tai"
LABEL email "gogistics@gogistics-tw.com"

# copy required files into img
COPY ./fans/fan /app
COPY ./infra/dumb-init /usr/bin/dumb-init

# run operations
RUN apk add --no-cache --virtual .build-deps g++ \
      python3-dev libffi-dev openssl-dev && \
  apk add --no-cache --update python3 && \
  pip3 install --upgrade pip setuptools && \
  cd /app && pip3 install pymongo redis && \
  chmod +x /usr/bin/dumb-init

WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "-u", "app.py"]