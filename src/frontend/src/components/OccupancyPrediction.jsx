import { useState, useEffect } from 'react';
import { Bar as BarChartforOccupancy } from 'react-chartjs-2';
import { Chart as ChartOccupancy, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import requestService from '../services/requestservice';

import Button from '@mui/material/Button';

// Registering Chart.js components
ChartOccupancy.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const GuestView = ({ fetchedBiowasteData, isLoadingBiowaste }) => {
  const [fetchedOccupancyData, setFetchedOccupancyData] = useState([]);
  const [isLoadingOccupancy, setIsLoadingOccupancy] = useState(true);
  const [titleForForecast, setTitleForForecast] = useState('Estimated Occupancy, Chemicum');
  const restaurants = ['Chemicum', 'Exactum', 'Physicum'];
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const [selectedRestaurant, setSelectedRestaurant] = useState('Chemicum');
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [selectedDay, setSelectedDay] = useState('Monday');
  const [selectedRestaurantIndex, setSelectedRestaurantIndex] = useState(0);
  const [dataOccupancy, setDataOccupancy] = useState();

  useEffect(() => {
    let ignoreOccupancy = false;
    const fetchData = async () => {
      try {
        const responseOccupancy = await requestService.getOccupancyOfRestaurantsByHour();
        if (!ignoreOccupancy) {
          const chemModified = Object.keys(responseOccupancy.data.Chemicum).map(key => responseOccupancy.data.Chemicum[key]).slice(0, 6);
          const chemDropEmptyHours = chemModified.map(arr => arr.slice(9, 16));
          const exaModified = Object.keys(responseOccupancy.data.Exactum).map(key => responseOccupancy.data.Exactum[key]).slice(0, 6);
          const exaDropEmptyHours = exaModified.map(arr => arr.slice(9, 16));
          const phyModified = Object.keys(responseOccupancy.data.Physicum).map(key => responseOccupancy.data.Physicum[key]).slice(0, 6);
          const phyDropEmptyHours = phyModified.map(arr => arr.slice(9, 16));
          setFetchedOccupancyData([chemDropEmptyHours, exaDropEmptyHours, phyDropEmptyHours]);
          setIsLoadingOccupancy(false);
        }
      } catch (error) {
        console.error('Error fetching occupancy data:', error);
      }
    };
    fetchData();
    return () => {
      ignoreOccupancy = true;
    };
  }, []);

  useEffect(() => {
    const createDataForChart = () => {
      if (isLoadingOccupancy) {
        setDataOccupancy(createDataSetToDisplay([30, 30, 30, 30, 30, 30, 30]));
      } else {
        const occupancy = fetchedOccupancyData[selectedRestaurantIndex][selectedDayIndex];
        setDataOccupancy(createDataSetToDisplay(occupancy));
      }
      setTitleForForecast(`Estimated Occupancy, ${selectedRestaurant}, ${selectedDay}`);
    };
    createDataForChart();
  }, [selectedRestaurant, selectedDay, selectedDayIndex, selectedRestaurantIndex, fetchedOccupancyData, isLoadingOccupancy]);

  const createDataSetToDisplay = (dataToShow) => ({
    labels: ['9-10', '10-11', '11-12', '12-13', '13-14', '14-15', '15-16'],
    datasets: [{
      label: 'Estimated Occupancy',
      borderColor: '#36A2EB',
      backgroundColor: '#155C2C',
      data: dataToShow,
    }]
  });

  const options = {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        min: 0,
        max: 250,
      }
    }
  };

  const handleRestaurantChange = (event, i) => {
    setSelectedRestaurant(event.currentTarget.value);
    setSelectedRestaurantIndex(i);
  };

  const handleDayChange = (event, day) => {
    setSelectedDayIndex(event.currentTarget.value);
    setSelectedDay(day);
  };

  return (
      <div>

        <div className="cardoccupancy">
          <h5 style={{ fontSize: '18px', fontWeight: 'bold' }}>{titleForForecast}</h5>
          {isLoadingOccupancy ? (
            <div>Loading...</div>
          ) : (
            <BarChartforOccupancy options={options} data={dataOccupancy} />
          )}
        </div>

        <div className="buttons">

          <div className="buttonsrow">
            {restaurants.map((restaurant, i) => (
              <Button
              variant="contained"
              sx={{
                bgcolor: '#485460',
                "&:hover": { bgcolor: '#1C1C1C', color: 'white' }
              }}
                size="large"
                key={i}
                value={restaurant}
                onClick={(event) => handleRestaurantChange(event, i)}
              >
                {restaurant}
            </Button>

              
            ))}
          </div>
          <div className="buttonsrow">
            {days.map((day, i) => (
              <Button
                variant="contained"
                sx={{
                  bgcolor: '#485460',
                  "&:hover": { bgcolor: '#1C1C1C', color: 'white' }
                }}
                size="large"
                key={day}
                value={i}
                onClick={(event) => handleDayChange(event, day)}
              >
                {day}
              </Button>
            ))}
          </div>

        </div>

      </div>
  );
};

export default GuestView;
