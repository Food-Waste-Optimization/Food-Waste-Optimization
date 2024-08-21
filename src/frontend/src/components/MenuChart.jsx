import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react'
import { useState, useEffect } from 'react'
import Unauthorized from './Unauthorized'
import 'bulma/css/bulma.min.css'

// Component creating individual charts presented on MenuView.jsx.

const MenuChart = ({ fetchedMenuData, isLoadingMenuData, Chart, Doughnut }) => {
    const [ titleForData, setTitleForData ] = useState('Estimated Occupancy, Chemicum')
    const restaurants = ['Chemicum', 'Exactum', 'Physicum', 'Total'] // used for buttons
    const quartals = ['Q123', 'Q223', 'Q323', 'Q423']               // used for buttons
    const dataUnloaded = {                              // placeholder for data when it is not loaded yet
        labels: ['Fish', 'Chicken', 'Meat', 'Vegan'],
        datasets: [{
            label: 'Estimated occupancy by hour',
              data: [],
              borderWidth: 1
            }]
        }
    const [ selectedRestaurant, setSelectedRestaurant ] = useState('Chemicum')
    const [ selectedQuartal, setSelectedQuartal ] = useState('Q123')
    const [ dataToDisplay, setDataToDisplay ] = useState(dataUnloaded)

    useEffect(() => {
        const createDataForChart = () => {
          if (isLoadingMenuData) {
            setDataToDisplay(createDataSetToDisplay([10, 10, 10, 10])) // using dummy data before the real one is loaded
          } else {
            const data1 = fetchedMenuData[selectedRestaurant][selectedQuartal] // setting up real data
            const dataset = createDataSetToDisplay(data1)
            setDataToDisplay(dataset)
        }
      }
        createDataForChart()
        setTitleForData(`Division of Menu Items, ${selectedRestaurant}, ${selectedQuartal}`)                     
      }, [selectedRestaurant, selectedQuartal, fetchedMenuData, isLoadingMenuData])

    // Helper function for setting up data displayed by state variables and use effect - loop
    const createDataSetToDisplay = (dataToShow) => {
      const sum = dataToShow.reduce((a, b) => a+b)
      const percentages = dataToShow.map((value) => Math.round(((value/sum*100) * 10) / 10))
        return ({
                labels: [`Fish ${percentages[0]} %`, `Chicken ${percentages[1]} %`, `Meat ${percentages[2]} %`, `Vegan ${percentages[3]} %`],
                datasets: [{
                    label: 'Meals Sold in Quartal',
                      data: dataToShow,
                      borderWidth: 1,
                      backgroundColor: ['black', 'red', 'blue', 'yellow'],
                      borderColor: ['white'],
                    }]
        })
    }

    // If data is not loaded yet this is returned:
    if (isLoadingMenuData) {
        return ( 
            <div>Is Loading...</div>
        )
    }

    // options for doughnut
      const options = {
        aspectRatio: 1,
        responsive: true,
        cutout: '40%',
        radius: '90%',
    }

    // onClick - function to handle restaurant change
    const handleRestaurantChange = (event) => {
        setSelectedRestaurant(event.currentTarget.value)
    }

    // onClick - function to handle quartal change
    const handleQuartalChange = (event) => {
        setSelectedQuartal(event.currentTarget.value)
    }  

    // Returns title for data, doughnut chart for selected data, buttons for restaurants and quartals, and functions to handle button clicks.
    // Unauthenticated users see the component Unauthorized.jsx.
    return (
        <>
            <AuthenticatedTemplate>
            <div className="cell p-6 m-6">
            <div className="p-6 m-6"> 
                <h5 className="title is-5" id="title-of-data-2">{titleForData}</h5>
                <Doughnut options={options} data={dataToDisplay}></Doughnut>
            </div>
            <div className="buttons">
                { restaurants.map((restaurant, i) => {
                        return (
                      <button className='button is-link' key={i} value={restaurant} onClick={handleRestaurantChange}>{restaurant}</button>                                
                      )
                   })}                            
            </div>
            <div className="buttons">
            { quartals.map((quartal, i) => {
                return (
                  <button className='button is-link' key={i} value={quartal} onClick={handleQuartalChange}>{quartal}</button>                                
                  )
                })}                            
            </div>                               
            </div>
            </AuthenticatedTemplate>
            <UnauthenticatedTemplate>
                <Unauthorized></Unauthorized>
            </UnauthenticatedTemplate>
        </>


    )
}

export default MenuChart