import React, { useState, useEffect } from "react";
import { Box, CircularProgress } from "@mui/material";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function Stats({ mealDetails, restaurant }) {
  const [mealData, setMealData] = useState([]);
  const [loading, setLoading] = useState(true);

  const generateMealUrl = (date, mealIds) => {
    return `https://megasense-server.cs.helsinki.fi/fwowebserver/forecast/pos?restaurant=${restaurant}&date=${date}&meal_ids=${mealIds.join(
      ","
    )}`;
  };

  const fetchMealData = async (url, mealIds) => {
    try {
      const response = await fetch(url);
      const data = await response.json();
      const cleanedMeals = data.meals.map((meal) => ({
        co2: isNaN(meal.co2) ? 0 : meal.co2,
        pcs: isNaN(meal.pcs) ? 0 : meal.pcs,
        waste: isNaN(meal.waste) ? 0 : meal.waste,
        meal_id: meal.meal_id,
      }));

      return { mealIds, meals: cleanedMeals };
    } catch (error) {
      console.error("Error fetching meal data:", error);
      return { mealIds, meals: [] };
    }
  };

  useEffect(() => {
    const loadMealData = async () => {
      const allMealData = [];

      for (const mealForDay of mealDetails) {
        const { date, meal_ids } = mealForDay;

        for (const mealSet of meal_ids) {
          const url = generateMealUrl(date, mealSet);
          const fetchedData = await fetchMealData(url, mealSet);
          allMealData.push(fetchedData);
        }
      }

      setMealData(allMealData);
      setLoading(false);
    };

    if (mealDetails.length) {
      loadMealData();
    }
  }, [mealDetails, restaurant]);

  const calculateSums = (mealSet) => {
    let co2Sum = 0;
    let wasteSum = 0;
    let pcsSum = 0;

    mealSet.meals.forEach((meal) => {
      co2Sum += meal.co2 * meal.pcs;
      wasteSum += meal.waste * meal.pcs;
      pcsSum += meal.pcs;
    });

    return { co2Sum, wasteSum, pcsSum };
  };

  const prepareGraphData = () => {
    const co2Data = [];
    const wasteData = [];
    const pcsData = [];
    const labels = [];

    mealDetails.forEach((mealForDay, dayIndex) => {
      const { date, meal_ids } = mealForDay;

      const dayOfWeek = new Date(date).toLocaleString("en-us", {
        weekday: "long",
      });
      const weekNumber = Math.floor(dayIndex / 5) + 1;

      labels.push(`Week ${weekNumber} - ${dayOfWeek}`);

      meal_ids.forEach((mealSet, optionIndex) => {
        const mealDataForSet = mealData.find(
          (data) => JSON.stringify(data.mealIds) === JSON.stringify(mealSet)
        );

        if (mealDataForSet) {
          const { co2Sum, wasteSum, pcsSum } = calculateSums(mealDataForSet);

          if (!co2Data[optionIndex]) co2Data[optionIndex] = [];
          if (!wasteData[optionIndex]) wasteData[optionIndex] = [];
          if (!pcsData[optionIndex]) pcsData[optionIndex] = [];

          co2Data[optionIndex].push(co2Sum);
          wasteData[optionIndex].push(wasteSum);
          pcsData[optionIndex].push(pcsSum);
        }
      });
    });

    const datasets = [];
    const colors = [
      { co2: "#37474F", waste: "#E65100", pcs: "#1B5E20" },
      { co2: "#546E7A", waste: "#FB8C00", pcs: "#388E3C" },
      { co2: "#90A4AE", waste: "#FFB74D", pcs: "#66BB6A" },
    ];

    co2Data.forEach((data, optionIndex) => {
      datasets.push({
        label: `Option ${optionIndex + 1} - CO₂ (kg CO2e)`,
        data: data,
        backgroundColor: colors[optionIndex % colors.length].co2,
      });
    });

    wasteData.forEach((data, optionIndex) => {
      datasets.push({
        label: `Option ${optionIndex + 1} - Waste (kg)`,
        data: data,
        backgroundColor: colors[optionIndex % colors.length].waste,
      });
    });

    pcsData.forEach((data, optionIndex) => {
      datasets.push({
        label: `Option ${optionIndex + 1} - Total sold pieces`,
        data: data,
        backgroundColor: colors[optionIndex % colors.length].pcs,
      });
    });

    return { labels, datasets };
  };

  return (
    <div className="p-0">
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "500px",
          padding: "20px",
          boxSizing: "border-box",
        }}
      >
        {loading ? (
          <CircularProgress
            sx={{
              color: "#155C2C",
              marginLeft: "30px",
              marginTop: "30px",
            }}
          />
        ) : (
          <Bar
            data={prepareGraphData()}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                x: { stacked: false },
                y: { beginAtZero: true },
              },
              plugins: {
                tooltip: {
                  backgroundColor: "#ffffff",
                  titleColor: "#000000",
                  bodyColor: "#000000",
                },
              },
              layout: {
                padding: 10,
              },
            }}
          />
        )}
      </Box>
    </div>
  );
}
