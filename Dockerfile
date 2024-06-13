FROM node:18-alpine AS BUILD_FRONT

WORKDIR /app

COPY ./src/frontend/package.json .

RUN npm install

COPY ./src/frontend .

ENV VITE_API_BASE_URL_PROD=https://megasense-server.cs.helsinki.fi
ENV VITE_AUTHORITY=https://TrialTenantD8Wzr80S.ciamlogin.com/
ENV VITE_URI_PRODUCTION=https://megasense-server.cs.helsinki.fi/fwowebserver

#comment below line if you are testing locally
ENV VITE_CLIENT_ID_PRODUCTION=a39f19d3-3ade-4052-a4d4-b25651948ff5

# comment out below line for testing in local machine
#ENV VITE_CLIENT_ID_PRODUCTION=f48af26e-9964-4e6e-9706-6f53fab1d115
#ENV VITE_URI_PRODUCTION=http://localhost:5000/fwowebserver

RUN chmod -R 777 *

RUN npm run build-prod


### Building container for flask app

FROM python:3.9-slim

RUN pip3 install poetry==1.8.2

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Passing secrets
RUN --mount=type=secret,id=db_user \
  cat /run/secrets/db_user

RUN --mount=type=secret,id=db_password \
  cat /run/secrets/db_password

RUN --mount=type=secret,id=db_host \
  cat /run/secrets/db_host
  
RUN --mount=type=secret,id=db_name \
  cat /run/secrets/db_name

RUN --mount=type=secret,id=database_url \
  cat /run/secrets/database_url
#

COPY pyproject.toml poetry.lock ./

RUN poetry lock

RUN poetry install --without dev --no-root

COPY . .

COPY --from=BUILD_FRONT /app/dist/ /app/src/frontend/dist

RUN chmod -R 777 *

RUN poetry lock

RUN poetry install --without dev

EXPOSE 5000

CMD [ "poetry", "run" , "invoke", "start-production"]
