import React from "react";

import { Chart as ChartJS, defaults } from "chart.js/auto";

import TabMenu from "./components/TabMenu";
import UntanglingFooter from "./components/UntanglingFooter";

import "./App.css";

defaults.maintainAspectRatio = false;
defaults.responsive = true;

defaults.plugins.title.display = true;
defaults.plugins.title.align = "start";
defaults.plugins.title.font.size = 20;
defaults.plugins.title.color = "black";

export const App = () => {
  return (

    <div className="App">

      <div className="min-h-screen bg-grey-200">

        <TabMenu />

        <UntanglingFooter />

      </div>
      
    </div>
    
  );
};