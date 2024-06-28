### Push image to your repository on Docker Hub

this instruction is mainly for future developer.

Current image of this application is pushed and pulled to our docker hub [account](https://hub.docker.com/repository/docker/ohjelmistotuotantoprojekti/food-waste-optimization/general). It's logged in via our school email.

So, as new developer team of the project you have to create your own docker hub account and push images to or
pull it from your own repository. The current account may get shut down at any time.

### Instructions on moving image to new docker hub account

- Firstly, you create an account on docker hub and create a public repository
- Name it as you want
- Now modify Stage and Deploy github actions so that they login and push the image
to your own repository.
- Then modify the docker-compose.yml file on the megasense-server, so that images are pulled from
your newly created repository