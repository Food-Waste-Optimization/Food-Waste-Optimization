FROM node:18-alpine AS BUILD_FRONT

WORKDIR /app

COPY ./src/frontend/package.json .

RUN npm install

COPY ./src/frontend .


ENV VITE_AUTHORITY=https://TrialTenantD8Wzr80S.ciamlogin.com/
# ENV VITE_URI_PRODUCTION=https://megasense-server.cs.helsinki.fi/fwowebserver

#comment below line if you are testing locally
ENV VITE_CLIENT_ID_PRODUCTION=a39f19d3-3ade-4052-a4d4-b25651948ff5

# comment out below line for testing in local machine
#ENV VITE_CLIENT_ID_PRODUCTION=f48af26e-9964-4e6e-9706-6f53fab1d115
ENV VITE_URI_PRODUCTION=http://localhost:5000

RUN chmod -R 777 * && npm run build-prod

### Building container for flask app
FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1

RUN pip3 install poetry==1.8.2

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# defing variables
COPY pyproject.toml poetry.lock ./

RUN poetry lock && poetry install --without dev --no-root

COPY . .

COPY --from=BUILD_FRONT /app/dist/ /app/src/frontend/dist

RUN chmod -R 777 * && poetry lock && poetry install --without dev && \
find /app/src/frontend -mindepth 1 ! -regex '^/app/src/frontend/dist\(/.*\)?' -delete && \
rm -r /app/Documentation /app/README.md /app/docker-compose.yaml

EXPOSE 5000

CMD [ "poetry", "run" , "invoke", "start-production"]
