import { useState } from 'react'
import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import 'bulma/css/bulma.min.css'

const GuestView = ({ instance }) => {

    const [ dataToDisplay, setDataToDisplay ] = useState([22.5, 43.2, 55.6, 23.7, 36.4])
    const data_for_chemicum = [22.5, 43.2, 55.6, 23.7, 36.4]
    const data_for_exactum = [13.6, 31.3, 18.9, 42.2, 11.7]
    const total = [36.1, 74.5, 74.5, 65.9, 48.1]
    const [ titleForForecast, setTitleForForecast ] = useState('Estimated Amount of Something, Chemicum')
 
    ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

    const data = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [{
            label: 'Predicted Bio Waste / kg',
              data: dataToDisplay,
              borderWidth: 1
            }]
        }

    const options = {
        responsive: true,
        scales: {
        y: {
          beginAtZero: true
        }
      }
    }
          
      const clickChemicum = () => {
        setTitleForForecast('Estimated Amount of Food Waste, Chemicum')
        setDataToDisplay(data_for_chemicum)
      }

      const clickExactum = () => {
        setTitleForForecast('Estimated Amount of Food Waste, Exactum')          
        setDataToDisplay(data_for_exactum)
      }

      const clickTotal = () => {
        setTitleForForecast('Estimated Amount of Food Waste, Total')          
        setDataToDisplay(total)
      }

    return (
      <>
        <div className="pt-3">
            <div className="container is-max-desktop">
                <div className="pt-6 pb-6">
                    <div className="p-4">
                        <h5 className="title is-5" id="title-of-forecast-1">{titleForForecast}</h5>
                        <Bar options={options} data={data}></Bar>           
                    </div>
                    <div className="buttons">
                      <button className="button is-link is-light" onClick={clickChemicum}>Chemicum</button>
                      <button className="button is-link is-light" onClick={clickExactum}>Exactum</button>
                      <button className="button is-link is-light" onClick={clickTotal}>Total</button>
                    </div>
                </div>
            </div>
        </div>
      </>
    )
}

export default GuestView