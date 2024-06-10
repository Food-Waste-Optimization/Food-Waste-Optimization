FROM node:18-alpine AS BUILD_FRONT

WORKDIR /app

COPY ./src/frontend/package.json .

RUN npm install

COPY ./src/frontend .

RUN chmod -R 777 *

RUN npm run build-prod

FROM python:3.9-slim

WORKDIR /app

COPY . .

COPY --from=BUILD_FRONT /app/dist/ /app/src/frontend/dist

RUN chmod -R 777 *

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip3 install poetry

RUN poetry lock

RUN poetry install

EXPOSE 5000

CMD [ "poetry", "run" , "invoke", "start-production"]
