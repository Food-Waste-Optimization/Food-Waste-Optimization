### Building container for flask app
FROM python:3.9-slim

WORKDIR /app
# ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip3 install poetry==1.8.2

# defing variables
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_NAME
#

ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_NAME=${DB_NAME}

ENV DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}/${DB_NAME}

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1

COPY pyproject.toml poetry.lock ./

RUN poetry lock && poetry install --without dev --no-root

# COPY . .

# COPY --from=BUILD_FRONT /app/dist/ /app/src/frontend/dist

# RUN find /app/src/frontend -mindepth 1 ! -regex '^/app/src/frontend/dist\(/.*\)?' -delete &&
# RUN rm -r /app/Documentation /app/README.md /app/docker-compose.yaml

EXPOSE 5000

ENTRYPOINT ["bash", "/app/run.sh"]
# ENTRYPOINT [ "tail", "-f", "/dev/null" ]
