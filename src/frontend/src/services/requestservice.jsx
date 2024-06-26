import axios from 'axios'

// Setting up routes depending on environment:

let base_api_url= ``

if(import.meta.env.DEV)
    base_api_url = 'http://127.0.0.1:5000'
else
    base_api_url = 'https://megasense-server.cs.helsinki.fi/fwowebserver'

const dataApi = `${base_api_url}/api/data`

// get-request used on testing:
const getDataFromFlask = async () => {
    const result = await axios.get(dataApi)
    console.log(result)
    return result
}

// Request to fetch data of occupancy presented on GuesView.jsx:
const getOccupancyOfRestaurantsByHour = async () => {
    const result = await axios.get(`${base_api_url}/data/occupancy`)
    console.log('getOccupancyOfRestaurantsByHour: ', result)
    return result
}

// Request to fetch data of biowaste. Presented partly (customer biowaste) on GuestView.jsx and fully on ManagerView.jsx:
const getBiowastePrediction = async () => {
    const result = await axios.get(`${base_api_url}/data/biowaste`)
    console.log('getBiowastePrediction: ', result)
    return result
}

// Request to fetch data of division of sold meals. Presented on MenuView.jsx:
const getDataForMenus = async () => {
    const result = await axios.get(`${base_api_url}/data/menus`)
    console.log('getDataForMenus: ', result)
    return result
}

export default {
    getDataFromFlask,
    getOccupancyOfRestaurantsByHour,
    getBiowastePrediction,
    getDataForMenus
}