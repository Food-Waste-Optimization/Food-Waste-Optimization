import { useState, useEffect } from 'react'
import OccupancyforGuests from './OccupancyforGuests'
import BiowasteforGuests from './BiowasteforGuests'
import requestService from '../services/requestservice'
import 'bulma/css/bulma.min.css'

const GuestView = ({ fetchedBiowasteData, isLoadingBiowaste }) => {

  // Component to present occupancy data of restaurants and estimated amount of biowaste / day / restaurant.
  // Indexes in occupancy data matrix used to present restaurants: Chemicum - 0, Exactum - 1, Physicum - 2
  // Indexes in occupancy data matrix used to present weekdays: 0 - Monday, 1 - Tuesday, 2 - Wednesday, 3 - Thursday, 4 - Friday, 5 - Saturday

    const [ fetchedOccupancyData, setFetchedOccupancyData ] = useState([])  // variables containing all fetched occupancy data
    const [ isLoadingOccupancy, setIsLoadingOccupancy ] = useState(true)


    useEffect(() => {
      let ignoreOccupancy = false
      const fetchData = async () => {
        try {
          const responseOccupancy = await requestService.getOccupancyOfRestaurantsByHour()
          console.log(responseOccupancy.data)
          if (!ignoreOccupancy) {
            const chemModified = Object.keys(responseOccupancy.data.Chemicum).map(key => responseOccupancy.data.Chemicum[key]).slice(0, 6)
            const chemDropEmptyHours = chemModified.map(arr => arr.slice(9, 16))
            const exaModified = Object.keys(responseOccupancy.data.Exactum).map(key => responseOccupancy.data.Exactum[key]).slice(0, 6)
            const exaDropEmptyHours = exaModified.map(arr => arr.slice(9, 16))
            const phyModified = Object.keys(responseOccupancy.data.Physicum).map(key => responseOccupancy.data.Physicum[key]).slice(0, 6)
            const phyDropEmptyHours = phyModified.map(arr => arr.slice(9, 16))  
            setFetchedOccupancyData([chemDropEmptyHours, exaDropEmptyHours, phyDropEmptyHours])
            setIsLoadingOccupancy(false)
          }
        } catch (error) {
          console.error('Error fetching occupancy data:', error)
        }
      }
      fetchData()
      return () => {
        ignoreOccupancy = true
      }
    }, [])
    
    return (
      <>
          <OccupancyforGuests fetchedOccupancyData={fetchedOccupancyData} isLoadingOccupancy={isLoadingOccupancy}>
            </OccupancyforGuests>
          <BiowasteforGuests fetchedBiowasteData={fetchedBiowasteData} isLoadingBiowaste={isLoadingBiowaste}>
          </BiowasteforGuests>                
      </>
    )
}

export default GuestView