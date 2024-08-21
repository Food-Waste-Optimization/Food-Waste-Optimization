import { useState, useEffect } from 'react'
import { Bar as BarChartforOccupancy } from 'react-chartjs-2'
import { Chart as ChartOccupancy, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import 'bulma/css/bulma.min.css'

const OccupancyforGuests = ({ fetchedOccupancyData, isLoadingOccupancy }) => {

  // Component to present occupancy data of restaurants and estimated amount of biowaste / customer.
  // Indexes in occupancy data matrix used to present restaurants: Chemicum - 0, Exactum - 1, Physicum - 2
  // Indexes in occupancy data matrix used to present weekdays: 0 - Monday, 1 - Tuesday, 2 - Wednesday, 3 - Thursday, 4 - Friday, 5 - Saturday


  const [ titleForForecast, setTitleForForecast ] = useState('Estimated Occupancy, Chemicum')
  const restaurants = ['Chemicum', 'Exactum', 'Physicum'] // used to dynamically create buttons
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] // used to dynamically create buttons
  const [ selectedRestaurant, setSelectedRestaurant ] = useState('Chemicum')
  const [ selectedDayIndex, setSelectedDayIndex ] = useState(0)
  const [ selectedDay, setSelectedDay ] = useState('Monday')
  const [ selectedRestaurantIndex, setSelectedRestaurantIndex ] = useState(0)
  const [ dataOccupancy, setDataOccupancy ] = useState()

  ChartOccupancy.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

  useEffect(() => {
    const createDataForChart = () => { 
      if (isLoadingOccupancy) {        // sets up dummy data while data is still being fetched
        setDataOccupancy(createDataSetToDisplay([30, 30, 30, 30, 30, 30, 30]))
      } else {
        const occupancy = fetchedOccupancyData[selectedRestaurantIndex][selectedDayIndex] // sets up the view when data has arrived
        setDataOccupancy(createDataSetToDisplay(occupancy))
    }
  }
  createDataForChart()
  setTitleForForecast(`Estimated Occupancy, ${selectedRestaurant}, ${selectedDay}`)
}, [selectedRestaurant, selectedDay, selectedDayIndex, selectedRestaurantIndex, fetchedOccupancyData, isLoadingOccupancy]) // dependencies: use effect - loop updates the view when a dependecy changes

// Helper function to set data in the right format for chart:
const createDataSetToDisplay = (dataToShow) => {
  return ({
      labels: ['9-10', '10-11', '11-12', '12-13', '13-14', '14-15', '15-16'],
      datasets: [{
          label: 'Estimated Occupancy',
          borderColor: '#36A2EB',
          backgroundColor: '#9BD0F5',
          data: dataToShow,
          borderWidth: 1,
        }]
    })
}

// this is returned if no data has arrived yet
if (isLoadingOccupancy) {
  return <div>Is loading...</div>
}

// options for the chart
  const options = {
      responsive: true,
      scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  // onClick-function to set up chosen restaurant
  const handleRestaurantChange = (event, i) => {   
    setSelectedRestaurant(event.currentTarget.value)
    setSelectedRestaurantIndex(i)
  }

  // onClick-function to set up chosen day
  const handleDayChange = (event, day) => {
    setSelectedDayIndex(event.currentTarget.value)
    setSelectedDay(day)
  }

  // Returns a title for forecast, a chart displaying occupancy data, a list of buttons with restaurant names and a list of buttons with weekdays.
    return (
      <div className="pt-3">
          <div className="container is-max-desktop">
              <div className="pt-6 pb-6">
                <div className="p-4"> 
                    <h5 className="title is-5" id="title-of-forecast-1">{titleForForecast}</h5>
                    <BarChartforOccupancy options={options} data={dataOccupancy}></BarChartforOccupancy>           
                </div>
                  <div className="buttons">
                    { restaurants.map((restaurant, i) => {
                        return (
                          <button className='button is-link' key={i} value={restaurant} onClick={(event) => handleRestaurantChange(event, i)}>{restaurant}</button>                                
                          )
                        })}                            
                      </div>
                      <div className="buttons">
                        { days.map((day, i) => {
                          return (
                            <button className='button is-link' key={day} value={i} onClick={(event) => handleDayChange(event, day)}>{day}</button>
                          )
                        })}
                      </div>
                </div>
            </div>
     </div>
  )
}

export default OccupancyforGuests
