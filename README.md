# Optimizing Food Waste Reduction  

![GHA workflow badge](https://github.com/Food-Waste-Optimization/Food-Waste-Optimization/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/Food-Waste-Optimization/Food-Waste-Optimization/graph/badge.svg?token=62FTEI7EG0)](https://codecov.io/gh/Food-Waste-Optimization/Food-Waste-Optimization)

This project is part of the summer 2024 Software Engineering project course [TKT20007](https://github.com/HY-TKTL/TKT20007-Ohjelmistotuotantoprojekti/) at the University of Helsinki. 

The aim of the project is to develop an AI-driven food demand forecasting service to address the challenges of food waste and optimize inventory management. The system will utilize multiple sources of various data to model demand.

Because the project is coursework, it is not possible to contribute outside the [project team](https://github.com/orgs/Food-Waste-Optimization/people) at this time.

## Development team resources
### Links
- [Shared Google drive](https://drive.google.com/drive/folders/1t-KEVXxDFisIF6f4bnrSdce5x8a1yYts)
- [Default meeting](https://helsinki.zoom.us/j/68765594737?pwd=Z1lELzNsWlh1cldtcGFGeEoxZ0JWZz09) on Zoom
- [Timesheets](https://study.cs.helsinki.fi/projekti/timelogs)
- Team [availability](https://docs.google.com/spreadsheets/d/13Yey7ICnYVVUK0rfN_uN6dhl0YFSL-u4YQSJD6pJmns)
<!---
- [Staging server](Megasense link here, as soon as authentication works reasonably)
--->

### Documentation
- [General](Documentation/general_practices.md)
- [Coding](Documentation/programming_practices.md)
- [Branching](Documentation/branching_practices.md)
- [Making commits](Documentation/commit_practices.md)
- [Definition of Done](Documentation/dod.md)


### Installation & Running Instructions
<!--- 
You can run the project locally in a [Docker](https://www.docker.com/) container.

- Download the code and make sure you have all the needed dependencies installed
- `docker-compose build` will build the containers. This needs to be run after changes in code.
- `docker-compose up` will start the containers. you probably need to exit with `CTRL-C` to get back to shell. This should also stop the containers, but not remove them or remove the docker container network.
- The system will print out URLs to try.
- `docker-compose down` will stop the containers and remove containers & container network.
--->
Currently it is not possible to run the containers locally, but we are looking at returning this option at a later time.
- [Instructions](Documentation/start_instructions.md) for running in local non-container development environment. (Project team only, as this needs current data files.)
  
### Further information
<!---
Current [live system](Megasense link here, as soon as authentication works reasonably)
--->
- Currently added extensions:
  - flask-cors
- [Tech Stack](Documentation/tech_stack.md)
