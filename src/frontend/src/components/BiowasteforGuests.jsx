import { useState, useEffect } from 'react'
import { Bar as BarChartforBiowaste } from 'react-chartjs-2'
import { Chart as ChartBiowaste, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import 'bulma/css/bulma.min.css'

// Component for presenting customer biowaste. Receives fetched data from App.jsx -> GuestView.jsx as props

const BiowasteforGuests = ({ fetchedBiowasteData, isLoadingBiowaste }) => {

  // Different chart names (eg. ChartBiowaste instead of Chart) are used to prevent conflicts while displaying several charts on the same view:
    ChartBiowaste.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

      const [ titleForForecast, setTitleForForecast ] = useState('Estimated Biowaste / Customer, Chemicum')
      const restaurants = ['Chemicum', 'Exactum', 'Physicum']     // list used to create buttons dynamically
      const [ selectedRestaurant, setSelectedRestaurant ] = useState('Chemicum')  // Name of selected Restaurant.
      const [ selectedRestaurantIndex, setSelectedRestaurantIndex ] = useState(0)  // Index for selected restaurant. 0: Chemicum, 1: Exactum, 2: Physicum. Data structure requires both name and index
      const [ dataBiowaste, setDataBiowaste ] = useState(({
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        datasets: [{
              label: 'Estimated Occupancy',
              borderColor: '#36A2EB',
              backgroundColor: '#9BD0F5',
              data: [5, 5, 5, 5, 5, 5],
              borderWidth: 1,
            }]
        }))

      useEffect(() => {
        const createDataForChart = () => {
          if (isLoadingBiowaste) {     // state while data is still loading and accessing it would cause error
            setDataBiowaste(createDataSetToDisplay([5, 5, 5, 5, 5, 5]))
          } else {     // setting the real state for chart when data is loaded
            const biowaste = fetchedBiowasteData[selectedRestaurantIndex][selectedRestaurant]
            setDataBiowaste(createDataSetToDisplay(biowaste))
        }
      }
      createDataForChart()
      setTitleForForecast(`Estimated Biowaste / Customer, ${selectedRestaurant}`)
    }, [selectedRestaurant, selectedRestaurantIndex, fetchedBiowasteData, isLoadingBiowaste]) // dependencies for use effect hook: the state is updated when one of the dependencies change.
    
    // Helper function to set up data in right format for the chart
    const createDataSetToDisplay = (dataToShow) => {
      return ({
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        datasets: [{
              label: 'Estimated Occupancy',
              borderColor: '#36A2EB',
              backgroundColor: '#9BD0F5',
              data: dataToShow,
              borderWidth: 1,
            }]
        })
    }

    // if data is not loaded this is returned to prevent errors caused by accessing undefined data:
    if (isLoadingBiowaste) {
      return <div>Is loading...</div>
    }
    
    // options for chart
      const options = {
          responsive: true,
          scales: {
          y: {
            beginAtZero: true
          }
        }
      }

     // function to handle button clicks and to change the selected restaurant
      const handleRestaurantChange = (event, i) => {    
        setSelectedRestaurant(event.currentTarget.value)
        setSelectedRestaurantIndex(i)
      }

    // Returns the chart, title for it, a dynamically created list of buttons presenting restaurant names and a function handling restaurant change.
    return (
        <div className="pt-3">
            <div className="container is-max-desktop">
             <div className="pt-6 pb-6">
                <div className="p-4"> 
                    <h5 className="title is-5" id="title-of-forecast-2">{titleForForecast}</h5>
                    <BarChartforBiowaste options={options} data={dataBiowaste}></BarChartforBiowaste>
                 </div>
                          <div className="buttons">
                            { restaurants.map((restaurant, i) => {
                              return (
                                <button className='button is-link' key={i} value={restaurant} onClick={(event) => handleRestaurantChange(event, i)}>{restaurant}</button>                                
                              )

                            })}                            
                          </div>
               </div>
            </div>
         </div>         
    )
}

export default BiowasteforGuests