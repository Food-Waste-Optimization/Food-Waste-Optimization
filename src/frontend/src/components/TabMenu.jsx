
import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import { styled } from '@mui/material/styles';

import LandingPage from './LandingPage.jsx';
import WastePredictionForm from "./WastePredictionForm.jsx"


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
        <Box sx={{ p: 4 }}>
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

  return (
    
    <div className='menu'>

      <CustomTabs value={value} onChange={handleChange}>
        <CustomTab label="About" />
        <CustomTab label="Daily waste prediction" />
        <CustomTab label="Hourly occupancy prediction" />
      </CustomTabs>

      <CustomTabPanel value={value} index={0}>
        <LandingPage />
      </CustomTabPanel>

      <CustomTabPanel value={value} index={1}>
        <WastePredictionForm />
      </CustomTabPanel>

      <CustomTabPanel value={value} index={2}>
        occupancy prediction will go here
      </CustomTabPanel>

    </div>

  );
}