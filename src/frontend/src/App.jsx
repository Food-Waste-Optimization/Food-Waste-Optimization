import { useState, useEffect } from 'react'
import { MsalProvider } from '@azure/msal-react'
import { Routes, Route, useNavigate } from "react-router-dom"
import { CustomNavigationClient } from "./utils/NavigationClient.js"
import requestService from './services/requestservice.jsx'
import Menu from './components/Menu.jsx'
import MenuView from './components/MenuView.jsx'
import AdminView from './components/AdminView.jsx'
import UploadView from './components/UploadView.jsx'
import Footer from './components/Footer.jsx'
import ManagerView from './components/ManagerView.jsx'
import GuestView from './components/GuestView.jsx'
import 'bulma/css/bulma.min.css'

const App = ({ instance }) => {

   // The next 3 lines are optional. This is how you configure MSAL to take advantage of the router's navigate functions when MSAL redirects between pages in your app
   // The configuration of Navigation Client is available on /utils - folder. More info on Navigation Client and react-router & MS Authentication available here:
   // https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/dev/lib/msal-react/docs/performance.md

  const navigate = useNavigate()
  const navigationClient = new CustomNavigationClient(navigate)
  instance.setNavigationClient(navigationClient)

  const [predData, setData] = useState(999)
  const [ fetchedBiowasteData, setFetchedBiowasteData ] = useState([]) // variables containing all fetched biowaste data
  const [ isLoadingBiowaste, setIsLoadingBiowaste ] = useState(true)
  const [ fetchedMenuData, setFetchedMenuData ] = useState([])  // variables containing all fetched data on menu items
  const [ isLoadingMenuData, setIsLoadingMenuData ] = useState(true)

  // data is fetched on useEffect-loop through /services/requestservice.jsx
  // ignore-variables are used to clean up after effect to prevent React.StrictMode to update everything twice while on dev-mode

  useEffect(() => {
    let ignore = false
    let ignoreBiowaste = false
    let ignoreMenus = false
    const fetchData = async () => {
      try {
        const response = await requestService.getDataFromFlask()
        if (!ignore) {
          setData(response.data)          
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      }
      try {
        const responseBiowaste = await requestService.getBiowastePrediction()
        if (!ignoreBiowaste) {
          setFetchedBiowasteData(responseBiowaste.data)
          setIsLoadingBiowaste(false)
        }
      } catch (error) {
        console.log('Error fetching biowaste data: ', error)
      }
      try {
        const responseMenus = await requestService.getDataForMenus()
        if (!ignoreMenus) {
          setFetchedMenuData(responseMenus.data)
          setIsLoadingMenuData(false)
        }
      } catch (error) {
        console.log('Error fetching data for menus: ', error)
      }
    }
    fetchData()
    return () => {
      ignore = true
      ignoreBiowaste = true
      ignoreMenus = true
    }
  }, [])

  // Helper variable to define routes differently while running on server or locally on development mode:

  const MODE = import.meta.env.MODE

  // Routes are defined here. MsalProvider and Router - tags have to be in this order. Data is passed to components as props, as well as
  // isLoading variables. The components handling log in and log out must have access to msalInstance.

  return (
    <>
    <MsalProvider instance={instance}>
      <Menu instance={instance}></Menu>
      <Routes>
            <Route path={ MODE == 'development' ? "/" : "/fwowebserver"} element={<GuestView instance={instance} fetchedBiowasteData={fetchedBiowasteData.customerBiowaste} isLoadingBiowaste={isLoadingBiowaste}/>} />
            <Route path="/fwowebserver" element={<GuestView instance={instance} fetchedBiowasteData={fetchedBiowasteData.customerBiowaste} isLoadingBiowaste={isLoadingBiowaste}/>} />
            <Route path={ MODE == 'development' ? "/sales" : "/fwowebserver/sales"} element={<ManagerView predData={predData} isLoadingBiowaste={isLoadingBiowaste} fetchedBiowasteData={fetchedBiowasteData}/>} />
            <Route path={ MODE == 'development' ? "/menus" : "/fwowebserver/menus"} element={<MenuView fetchedMenuData={fetchedMenuData} isLoadingMenuData={isLoadingMenuData}/>} />
            <Route path={ MODE == 'development' ? "/admin" : "/fwowebserver/admin"} element={<AdminView />} />
            <Route path={ MODE == 'development' ? "/upload" : "/fwowebserver/upload"} element={<UploadView />} />
        </Routes>
      <Footer></Footer>      
    </MsalProvider>
    </>
  )

}

export default App
