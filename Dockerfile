FROM node:18-alpine AS build-front

WORKDIR /build

ENV VITE_AUTHORITY=https://TrialTenantD8Wzr80S.ciamlogin.com/
ENV VITE_CLIENT_ID_PRODUCTION=f48af26e-9964-4e6e-9706-6f53fab1d115
ENV VITE_URI_PRODUCTION=http://localhost:1000/fwowebserver

COPY src/frontend/ /build
RUN npm install
RUN npm run build-prod

### Building container for flask app
FROM python:3.9-slim

WORKDIR /app

COPY . .
COPY --from=build-front /build/dist/ /build/dist

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1

RUN pip3 install poetry==1.8.2

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry lock && poetry install --without dev --no-root

CMD [ "poetry", "run" , "invoke", "start-production"]
# CMD [ "sleep", "infinity" ]
