## Megasense Server

#### What is it?
 
 Megasense is a data platform owned by the Department of the Computer Science at the University of Helsinki where
 data is hosted and provided via Megasense API to users.
 Megasense provides a server for hosting, preferably containerized, applications.
 
 We use megasense as both production and staging environment for the application.

 #### Access to Megasense

 In order to get access using megasense-server, you have to ask for permissions by sending email to the megasense administrative contact person. You will know who this is, if you are a member of the development team needing access to megasense.

 Having permissions to use platform, you can login to using SSH command line tool from linux/MacOS/Win. SSH would be the easiest, although not user friendly, way of using megasense-server.

 To login using ssh use following command:
  `ssh username@megasense-server.cs.helsinki.fi`


 #### Checking out Application on Megasense Server
 
 Our fullstacked application is running in docker container named as **fwowebserver**. The application
 is tracked and gets updated automatically on an hourly basis using **watchtower** tool. Watchtower simply checks each hour whether a new version of image of our application is available in DockerHub and pulls it out, builds it and finally run it again with the same name.

 You can find docker-compose.yml and data folder from the home directory of the machine's user. When logged in
 you can navigate to the destination folder with following command.
 - `sudo cd /home/tkt_msns/fwo`



#### How is it even configured?

 Docker runs constantly the containers available inside megasense-server. We have created a docker-compose.yml file which defines four services as following:
 
 - **fwoapp**: main application containes both backend and frontend (stage-environment).
 - **watchtower**: pull in application image from Docker Hub registery on hourly basis.
 - **fwo-ann**: Neural Network process training our model with the current dataset.
 - **fwofront**: Main application containing both frontend and backend (Production environment).

