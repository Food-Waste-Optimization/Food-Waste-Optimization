import { useState } from 'react';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import { styled } from '@mui/material/styles';

import LandingPage from './LandingPage.jsx';
import RecommendationDaily from './RecommendationDaily.jsx';
import RecommendationWeekly from './RecommendationWeekly';

import logofood from '../img/logo_foodwaste.png';

const CustomTabs = styled(Tabs)({
  '& .MuiTabs-indicator': {
    backgroundColor: '#155C2C',
  },
});

const CustomTab = styled(Tab)({
  '&.Mui-selected': {
    color: '#155C2C', 
  },
});

function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 1, px: 3 }}>
          <div>{children}</div>
        </Box>
      )}
    </div>
  );
}

export default function TabMenu() {
  const [value, setValue] = useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const handleSwitchTab = () => {
    setValue(1); 
  };

  return (

    <div className="min-h-screen bg-emerald-50 p-4">

      <div className="flex flex-col md:flex-row items-center justify-between px-4 pt-4 w-full">
     
        <div className="flex-grow mb-0 md:mb-0 pb-4">

          <CustomTabs
            value={value}
            onChange={handleChange}
            variant="scrollable"
            scrollButtons="auto"
            allowScrollButtonsMobile
          >
            <CustomTab label="About" />
            <CustomTab label="Weekly recommendation" />
            <CustomTab label="Daily recommendation" />
          </CustomTabs>

        </div>

        <div className="text-center md:text-right mb-4 md:mb-0">

          <h1 className="text-xl font-bold text-gray-800 leading-tight">Unicafe Food Waste Optimization</h1>

          <h3 className="text-lg text-gray-600 mt-2">AI-assisted recommendation system for meal planning in YLVA restaurants</h3>

        </div>

        <div className="flex items-center ml-4">

          <img src={logofood} width={68} alt="Food Logo" />

        </div>

      </div>

      <CustomTabPanel value={value} index={0}>
        <LandingPage onSwitchTab={handleSwitchTab} />
      </CustomTabPanel>

      <CustomTabPanel value={value} index={1}>
        <RecommendationWeekly />
      </CustomTabPanel>

      <CustomTabPanel value={value} index={2}>
        <RecommendationDaily />
      </CustomTabPanel>

    </div>

  );
}
