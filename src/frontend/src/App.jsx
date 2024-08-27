
import React from "react";

import { Chart as ChartJS, defaults } from "chart.js/auto";

import "./App.css";

import Header from "./components/Header";
import TabMenu from "./components/TabMenu";

defaults.maintainAspectRatio = false;
defaults.responsive = true;

defaults.plugins.title.display = true;
defaults.plugins.title.align = "start";
defaults.plugins.title.font.size = 20;
defaults.plugins.title.color = "black";

export const App = () => {
  return (

    <div className="App">

      <Header />

      <TabMenu />
      
    </div>
    
  );
};