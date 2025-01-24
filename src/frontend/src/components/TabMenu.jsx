import { useState } from "react";
import Box from "@mui/material/Box";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import { styled } from "@mui/material/styles";

import LandingPage from "./LandingPage.jsx";
import Dashboard from "./Dashboard";

import logofood from "../img/logo_foodwaste.png";

const CustomTabs = styled(Tabs)({
  "& .MuiTabs-indicator": {
    backgroundColor: "#155C2C",
  },
});

const CustomTab = styled(Tab)({
  "&.Mui-selected": {
    color: "#155C2C",
  },
});

function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
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
      <div className="flex items-center justify-start px-4 pt-1 w-full">
        {" "}
        <div className="flex items-center space-x-4 mb-4 md:mb-0">
          {" "}
          <div className="flex items-center">
            <img src={logofood} width={40} alt="Food Logo" />{" "}
          </div>
          <div className="text-left">
            <h1 className="text-lg font-bold text-[#155C2C] px-2 pt-2">
              {" "}
              YLVA AI Menu Planner
            </h1>
          </div>
          <div className="flex items-center space-x-2 pt-2">
            {" "}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="60"
              height="40"
              viewBox="-30 0 100 100"
              className="m-0"
            >
              <path
                d="M-20,50 C0,20, 30,20, 20,50 C10,80, -30,60, -20,50 Z"
                fill="#66BFA2"
              />
            </svg>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="50"
              height="40"
              viewBox="-30 0 100 100"
              className="m-0"
            >
              <path
                d="M-30,40 C-20,15, 20,15, 10,40 C0,65, -20,65, -30,40 Z"
                fill="#A3D9A5"
              />
            </svg>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="65"
              height="40"
              viewBox="-30 0 140 100"
              className="m-0"
            >
              <path
                d="M-30,30 C-20,5, 60,5, 40,30 C20,50, 0,70, -30,30 Z"
                fill="#C8E6C9"
              />
            </svg>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="50"
              height="40"
              viewBox="-30 0 100 100"
              className="m-0"
            >
              <path
                d="M-30,20 C-20,5, 10,5, 0,20 C-10,35, -30,30, -30,20 Z"
                fill="#D1E7DD"
              />
            </svg>
          </div>
        </div>
      </div>

      <Dashboard />
    </div>
  );
}
