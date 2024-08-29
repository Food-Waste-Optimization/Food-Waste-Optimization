
import { useState } from 'react';

import { Bar } from 'react-chartjs-2';

import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Slider from '@mui/material/Slider';
import { styled } from '@mui/material/styles';

import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers';

import dayjs from 'dayjs';


const initialValues = {
  chicken: 0,
  fish: 0,
  meat: 0,
  vegan: 0,
  vegetarian: 0,
  location: "Chemicum",
};

const minSelectableDate = dayjs('2024-05-09');

const disableWeekends = (date) => {
  const day = date.day(); 
  return day === 0 || day === 6; 
};

const CustomSlider = styled(Slider)(({ theme }) => ({
  color: 'black',
  height: 4,
  '& .MuiSlider-thumb': {
    height: 16,
    width: 16,
    backgroundColor: 'black',
    border: 'none',
    '&:focus': {
      boxShadow: 'none',
    },
  },
  '& .MuiSlider-track': {
    height: 4,
  },
  '& .MuiSlider-rail': {
    height: 4,
  },
  '& .MuiSlider-valueLabel': {
    backgroundColor: 'black',
    color: 'white',
    borderRadius: '4px',
  },
}));

const SliderWrapper = styled('div')(({ theme }) => ({
  marginBottom: 8,
}));

export default function WastePredictionForm() {
  const [values, setValues] = useState(initialValues);
  const [selectedDate, setSelectedDate] = useState(dayjs()); 
  const [chartData, setChartData] = useState({
    wasteFromCustomers: [0],
    wasteFromKitchen: [0],
    wastePerCustomer: [0],
    receipts: [0]
  });

  const handleInputChange = (name) => (event, newValue) => {
    setValues({
      ...values,
      [name]: newValue,
    });
  };

  const handleLocationChange = (event) => {
    setValues({
      ...values,
      location: event.target.value,
    });
  };

  const handleDateChange = (newValue) => {
    setSelectedDate(newValue);
  };

  const fetchData = async () => {
    const date = selectedDate.format('YYYY-MM-DD'); 
    const urlWaste = `https://megasense-server.cs.helsinki.fi/fwowebserver/forecast/biowaste_from_meals?restaurant=${values.location}&num_fish=${values.fish}&num_chicken=${values.chicken}&num_vegetarian=${values.vegetarian}&num_meat=${values.meat}&num_vegan=${values.vegan}&return_type=numeric&date=${date}`;
    const urlCarbonEmissions = `https://megasense-server.cs.helsinki.fi/fwowebserver/forecast/co2_from_meals?restaurant=${values.location}&num_fish=${values.fish}&num_chicken=${values.chicken}&num_vegetarian=${values.vegetarian}&num_meat=${values.meat}&num_vegan=${values.vegan}`

    try {
      const responseWaste = await fetch(urlWaste);
      const dataWaste = await responseWaste.json();
      const responseCarbonEmissions = await fetch(urlCarbonEmissions);
      const dataCarbonEmissions= await responseCarbonEmissions.json();

      setChartData({
        wasteFromCustomers: [dataWaste.predicted_waste_customer],
        wasteFromKitchen: [dataWaste.predicted_waste_kitchen],
        wastePerCustomer: [dataWaste.predicted_waste_per_customer],
        receipts: [dataWaste.predicted_num_receipts],
        carbonEmissions: [dataCarbonEmissions.predicted_co2]
      });
    } catch (error) {
      console.error("Error fetching data: ", error);
    }
  };

  return (
    
    <div>

      <div className="container">

        <form className="cardui">
          <br />
          <SliderWrapper>
            chicken
            <br />
            <CustomSlider
              value={values.chicken}
              onChange={handleInputChange("chicken")}
              name="chicken"
              min={0}
              max={300}
              aria-labelledby="chicken-slider"
              valueLabelDisplay="auto"
              step={10}        
              marks={true}     
            />
          </SliderWrapper>

          <SliderWrapper>
            fish
            <br />
            <CustomSlider
              value={values.fish}
              onChange={handleInputChange("fish")}
              name="fish"
              min={0}
              max={300}
              aria-labelledby="fish-slider"
              valueLabelDisplay="auto"
              step={10}        
              marks={true}     
            />
          </SliderWrapper>

          <SliderWrapper>
            meat
            <br />
            <CustomSlider
              value={values.meat}
              onChange={handleInputChange("meat")}
              name="meat"
              min={0}
              max={300}
              aria-labelledby="meat-slider"
              valueLabelDisplay="auto"
              step={10}        
              marks={true}     
            />
          </SliderWrapper>

          <SliderWrapper>
            vegan
            <br />
            <CustomSlider
              value={values.vegan}
              onChange={handleInputChange("vegan")}
              name="vegan"
              min={0}
              max={300}
              aria-labelledby="vegan-slider"
              valueLabelDisplay="auto"
              step={10}        
              marks={true}     
            />
          </SliderWrapper>

          <SliderWrapper>
            vegetarian
            <br />
            <CustomSlider
              value={values.vegetarian}
              onChange={handleInputChange("vegetarian")}
              name="vegetarian"
              min={0}
              max={300}
              aria-labelledby="vegetarian-slider"
              valueLabelDisplay="auto"
              step={10}        
              marks={true} 
            />
          </SliderWrapper>

          <FormControl fullWidth variant="outlined" sx={{ marginBottom: 2 }}>
            <Select
              id="location"
              value={values.location}
              onChange={handleLocationChange}
            >
              <MenuItem value="Chemicum"><b>Chemicum</b></MenuItem>
              <MenuItem value="Physicum"><b>Physicum</b></MenuItem>
              <MenuItem value="Exactum"><b>Exactum</b></MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth variant="outlined" sx={{ marginBottom: 4 }}>

            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DatePicker
              minDate={minSelectableDate} 
              shouldDisableDate={disableWeekends} 
              value={selectedDate}
              onChange={handleDateChange}          
              />
            </LocalizationProvider>

          </FormControl>

          <div className="cardinput">
            <Bar
              data={{
                labels: ['chicken', 'fish', 'meat', 'vegan', 'vegetarian'],
                datasets: [
                  {
                    label: "Meals",
                    data: [
                      values.chicken,
                      values.fish,
                      values.meat,
                      values.vegan,
                      values.vegetarian
                    ],
                    backgroundColor: [
                      "#eec591",
                      "#9dd4dd",
                      "#c9a8eb",
                      "#155C2C",
                      "#485460",
                    ],
                  },
                ],
              }}
              options={{
                plugins: {
                  title: {
                    display: true,
                    text: "Input Meals",
                  },
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    min: 0,
                    max: 350,
                  },
                },
              }}
            />
          </div>

          <Button
            variant="contained"
            sx={{
              bgcolor: '#155C2C',
              "&:hover": { bgcolor: '#1C1C1C', color: 'white' }
            }}
            size="large"
            onClick={fetchData}
          >
            Predict
          </Button>
        </form>

        <div class="chartswrapper">

        {chartData.receipts && (
            <div className="cardoutput">
              <Bar
                data={{
                  labels: ['Planned meals', 'Predicted receipts'],
                  datasets: [
                    {
                      label: "",
                      data: [
                        ([values.chicken + values.fish + values.meat + values.vegan + values.vegetarian])[0],
                        chartData.receipts[0],
                      ],
                      backgroundColor: [
                        "#d3e9bf",
                        "#155C2C",
                      ],
                    },
                  ],
                }}
                options={{
                  plugins: {
                    title: {
                      display: true,
                      text: "Number of planned meals vs predicted receipts",
                    },
                    legend: {
                      display: false,
                    },
                  },
                  scales: {
                    y: {
                      min: 0,
                      max: 800,
                    },
                  },
                }}
              />
            </div>
          )}

          {chartData.receipts && (
            <div className="cardoutput">
              <Bar
              data={{
                labels: ['Predicted carbon emissions (kg CO2e)'],
                datasets: [
                  {
                    label: "",
                    data: chartData.carbonEmissions,
                    backgroundColor: [
                      "#485460",
                    ],
                  },
                ],
              }}
              options={{
                plugins: {
                  title: {
                    display: true,
                    text: "Predicted carbon emissions (in kg CO2e)",
                  },
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    min: 0,
                    max: 1000,
                  },
                },
              }}
            />
            </div>
          )}     

          {chartData.wasteFromCustomers && (
            <div className="cardoutput">
              <Bar
                data={{
                  labels: ['Predicted customer waste (kg)', 'Predicted kitchen waste (kg)'],
                  datasets: [
                    {
                      label: "",
                      data: [
                        chartData.wasteFromCustomers[0],
                        chartData.wasteFromKitchen[0]
                      ],
                      backgroundColor: [
                        "#eec591",
                        "#9dd4dd",
                      ],
                    },
                  ],
                }}
                options={{
                  plugins: {
                    title: {
                      display: true,
                      text: "Predicted waste per type (in kilograms)",
                    },
                    legend: {
                      display: false,
                    },
                  },
                  scales: {
                    y: {
                      min: 0,
                      max: 60,
                    },
                  },
                }}
              />
            </div>
          )}

          {chartData.wastePerCustomer && (
            <div className="cardoutput">
              <Bar
                data={{
                  labels: ['Predicted waste per customer (g)'],
                  datasets: [
                    {
                      label: "",
                      data: chartData.wastePerCustomer,
                      backgroundColor: ["#c9a8eb"],
                    },
                  ],
                }}
                options={{
                  plugins: {
                    title: {
                      display: true,
                      text: "Predicted waste per customer (in grams)",
                    },
                    legend: {
                      display: false,
                    },
                  },
                  scales: {
                    y: {
                      min: 0,
                      max: 300,
                    },
                  },
                }}
              />
            </div>
          )}

          </div> 

        </div>

      </div>
  );
}
