import { useState, useEffect } from 'react'
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react'
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, LinearScale, ArcElement, Title, Tooltip, Legend } from 'chart.js'
import Unauthorized from './Unauthorized.jsx'
import 'bulma/css/bulma.min.css'

// Component to present data for managers: sales data, data on biowaste and possible others. Currently
// displaying only the full biowaste data (the same data is partly presented on GuestView.jsx)

const ManagerView = ({ fetchedBiowasteData, isLoadingBiowaste }) => {

    ChartJS.register(ArcElement, LinearScale, Title, Tooltip, Legend)

    const [ titleForForecast, setTitleForForecast ] = useState('Estimated Biowaste, Chemicum, Monday')
    const restaurants = ['Chemicum', 'Exactum', 'Physicum']  // used to dynamically create buttons
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']  // used to dynamically create buttons
    const [ selectedRestaurant, setSelectedRestaurant ] = useState('Chemicum') // These 4 variables are used to present the selected part
    const [ selectedDayIndex, setSelectedDayIndex ] = useState(0)              // of data based on user's choice.
    const [ selectedDay, setSelectedDay ] = useState('Monday')                 //
    const [ selectedRestaurantIndex, setSelectedRestaurantIndex ] = useState(0)//
    const [ dataToDisplay, setDataToDisplay ] = useState({
      labels: ['Coffee', 'Customer', 'Kitchen', 'Hall'],
      datasets: [{
          label: 'Estimated biowaste',
            data: [10, 10, 10, 10],  // dummy list used when actual data has not been loaded yet
            borderWidth: 1,
            backgroundColor: ['black', 'red', 'blue', 'yellow'],
            borderColor: ['white'],
          }]
      })

    useEffect(() => {
      const createDataForChart = () => {
        if (isLoadingBiowaste) { // setting up a placeholder while real data is fetched
          setDataToDisplay(      {
            labels: ['Coffee', 'Customer', 'Kitchen', 'Hall'],
            datasets: [{
                label: 'Estimated biowaste',
                  data: [10, 10, 10, 10], // dummy list
                  borderWidth: 1,
                  backgroundColor: ['black', 'red', 'blue', 'yellow'],
                  borderColor: ['white'],
                }]
            })
        } else { // setting up real data to display
          const coffee = fetchedBiowasteData.coffeeBiowaste[selectedRestaurantIndex][selectedRestaurant][selectedDayIndex]
          const customer = fetchedBiowasteData.customerBiowaste[selectedRestaurantIndex][selectedRestaurant][selectedDayIndex]
          const kitchen = fetchedBiowasteData.kitchenBiowaste[selectedRestaurantIndex][selectedRestaurant][selectedDayIndex]
          const hall = fetchedBiowasteData.hallBiowaste[selectedRestaurantIndex][selectedRestaurant][selectedDayIndex]
          const all = [coffee, customer, kitchen, hall]
          setDataToDisplay(
          {
            labels: ['Coffee', 'Customer', 'Kitchen', 'Hall'],
            datasets: [{
                label: 'Estimated biowaste',
                  data: all,
                  borderWidth: 1,
                  backgroundColor: ['black', 'red', 'blue', 'yellow'],
                  borderColor: ['white'],
                }]
            }
        )
      }
    }
      createDataForChart()
      setTitleForForecast(`Estimated Biowaste, ${selectedRestaurant}, ${selectedDay}`)
    }, [selectedRestaurant, selectedDay, selectedDayIndex, selectedRestaurantIndex, fetchedBiowasteData, isLoadingBiowaste]) // Dependencies for use effect - loop. The view is updated when one of the dependencies change

    // If data is not loaded yet, this is returned:
    if (isLoadingBiowaste) {
      return <div>Is loading...</div>
    }

    // options for the chart
    const options = {
        aspectRatio: 1,
        responsive: true,
        cutout: '40%',
        radius: '50%',
    }

    // onClick-function to handle selection of restaurant
    const handleRestaurantChange = (event, i) => {   
      setSelectedRestaurant(event.currentTarget.value)
      setSelectedRestaurantIndex(i)
    }

    // onClick-function to handle selection of day
    const handleDayChange = (event, day) => {
      setSelectedDayIndex(event.currentTarget.value)
      setSelectedDay(day)
    }

    // For authenticated users returns title of forecast, doughnut chart presenting a selection of data, dynamically created buttons, and functions for the buttons to update the view.
    // Unauthenticated users see the component Unauthorized.jsx
    return (
        <>
        <AuthenticatedTemplate>
        <div className="fixed-grid has-8-cols">
            <div className="grid">
                <div className="cell"></div>
                <div className="cell"></div>
                <div className="cell  is-col-span-4">
                    <h5 className="title is-5" id="title-of-forecast-1">{titleForForecast}</h5>
                    <Doughnut options={options} data={dataToDisplay}></Doughnut>
                    <div className="pt-3">

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
                <div className="cell"></div>
                <div className="cell"></div>
                <div className="cell"></div>
                <div className="cell"></div>
                <div className="cell"></div>
                </div>
        </AuthenticatedTemplate>
        <UnauthenticatedTemplate>
            <Unauthorized></Unauthorized>
        </UnauthenticatedTemplate>
    </>
    )
}

export default ManagerView