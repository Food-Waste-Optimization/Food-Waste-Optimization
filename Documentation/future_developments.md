# Possible Development Targets for Future

The current software structure and developmental phase allows several possible ways to advance further. Here are listed some of the ideas that came up during the development.

## Back End

- Utilising CO2-data in AI model, perhaps estimating CO2 per day  
- Improving AI model, exploratory testing to find better parameters and settings  
  - e.g. academic years and weeks, see see side project [ac_years_to_db](https://github.com/Food-Waste-Optimization/ac_years_to_db) and branch [day-info](https://github.com/Food-Waste-Optimization/Food-Waste-Optimization/tree/day-info)
- Improving NLP, it is quite heavy to run  

## Front End

- Front end structure currently has components for admin view and for data upload. Both of these lack functionality. If needed, these can be added later.  
- Improving chart sizes and layout. Also for different screen sizes.  

## Database

- Moving from test database to production database. This will allow more testing to be done with the test database without compromising production.  
- People flow data is not in the database
- Biowaste data is not fetched from the database
- Occupancy data (receipt data) is not fetched from the database
- User interface for data upload (see Front End)
- Using the information of the academic years (see side project [ac_years_to_db](https://github.com/Food-Waste-Optimization/ac_years_to_db))


## Testing

- The software is in need of much more testing. A big road block to testing is a successful database integration, which we were able to start at the end of the project, but it still needs some work.
- Model testing and cross-validation are not done currently.

## Other ideas

- More exploratory data analysis to provide value to YLVA, finding relations and causalities from data  
