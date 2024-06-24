# tuntidata.xlsx

- Significant hours (the hours which have the most) are 10 - 14
- Datetime is up to hour, range from 2023-Jan to 2024-May, in business day
- There are NaN values even in peak hour
- The quantity series in hour-10 to hour-14 share similarities:
  - Quite similar trending pattern
  - The quantity dips during Christmas and summer
- Using ACF plot, we see that:
  - Quantity is date-correlated, not hour-correlated: quantity at today 10am depends greatly on yesterday 10am
  - Quantity depends on last 5 days values of the same hours
