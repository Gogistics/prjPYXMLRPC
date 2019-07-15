FROM alpine:latest

LABEL maintainer "gogistics@gogistics-tw.com"

# copy required files into img
COPY ./subsystems/fan /app
COPY ./infra/requirements/fan.txt /app
COPY ./infra/dumb-init /usr/bin/dumb-init

# run operations
RUN apk update -y && \
  apk install -y curl python-pip python-dev build-essential && \
  pip install --upgrade pip && \
  cd /app && pip install -r requirements.txt && \
  chmod +x /usr/bin/dumb-init

WORKDIR /app
EXPOSE 8080
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
