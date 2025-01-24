import React, { useState, useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { Bar } from "react-chartjs-2";
import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels"; // Importing datalabels plugin

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels // Register the datalabel plugin
);

export default function Stats({ mealDetails, restaurant, selectedWeek }) {
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

  const prepareGraphData = (category) => {
    const data = [];
    const labels = [];
    const totalSums = []; // Array to store total sums for each option

    const filteredMealDetails = mealDetails.filter((mealForDay, dayIndex) => {
      const weekNumber = Math.floor(dayIndex / 5) + 1;
      return weekNumber === selectedWeek + 1;
    });

    filteredMealDetails.forEach((mealForDay, dayIndex) => {
      const { date, meal_ids } = mealForDay;

      const dayOfWeek = new Date(date).toLocaleString("en-us", {
        weekday: "long",
      });

      labels.push(dayOfWeek);

      meal_ids.forEach((mealSet, optionIndex) => {
        const mealDataForSet = mealData.find(
          (data) => JSON.stringify(data.mealIds) === JSON.stringify(mealSet)
        );

        if (mealDataForSet) {
          const { co2Sum, wasteSum, pcsSum } = calculateSums(mealDataForSet);

          if (!data[optionIndex]) data[optionIndex] = [];
          if (!totalSums[optionIndex]) totalSums[optionIndex] = 0; // Initialize total for this option

          if (category === "co2") {
            data[optionIndex].push(co2Sum);
            totalSums[optionIndex] += co2Sum; // Store total separately for this option
          } else if (category === "waste") {
            data[optionIndex].push(wasteSum);
            totalSums[optionIndex] += wasteSum;
          } else if (category === "pcs") {
            data[optionIndex].push(pcsSum);
            totalSums[optionIndex] += pcsSum;
          }
        }
      });
    });

    const datasets = [];
    const colors = [
      { co2: "#FFDDC1", waste: "#FFDDC1", pcs: "#FFDDC1" },
      { co2: "#FFE4B5", waste: "#FFE4B5", pcs: "#FFE4B5" },
      { co2: "#FAD02E", waste: "#FAD02E", pcs: "#FAD02E" },
    ];

    data.forEach((optionData, optionIndex) => {
      datasets.push({
        label: `Option ${optionIndex + 1}`,
        data: optionData,
        backgroundColor: colors[optionIndex % colors.length][category],
        barPercentage: 1, // Ensures the bars touch
      });
    });

    return { labels, datasets, totalSums }; // Return total sums separately per option
  };

  const co2Sums = prepareGraphData("co2").totalSums;
  const wasteSums = prepareGraphData("waste").totalSums;
  const salesSums = prepareGraphData("pcs").totalSums;

  const radarData = {
    labels: ["CO₂ Emissions (kg)", "Waste (kg)", "Total Sales (pcs)"],
    datasets: co2Sums.map((_, index) => ({
      label: `Option ${index + 1}`,
      data: [co2Sums[index], wasteSums[index], salesSums[index]],
      backgroundColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
        Math.random() * 255
      }, 0.2)`, // Generate different colors dynamically
      borderColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
        Math.random() * 255
      }, 1)`,
      borderWidth: 2,
    })),
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        width: "100%",
        padding: "0px",
        boxSizing: "border-box",
        gap: "20px", // Ensures spacing between the charts
      }}
    >
      {loading ? (
        <CircularProgress
          sx={{
            color: "#155C2C", // Custom green color for CircularProgress
            marginLeft: "30px",
            marginTop: "30px",
          }}
        />
      ) : (
        <>
          {/* Total Sales Chart */}
          <Box
            sx={{
              width: "100%", // Make Total Sales chart full width
              padding: "10px",
              height: "400px", // Fixed height for the chart
            }}
          >
            <Bar
              data={prepareGraphData("pcs")}
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
                  title: {
                    display: true,
                    text: "Forecasted Total Sales (pieces)",
                    font: {
                      size: 18,
                      weight: "bold",
                    },
                    color: "#333333",
                    padding: {
                      top: 10,
                      bottom: 20,
                    },
                    align: "center",
                  },
                  datalabels: {
                    display: true,
                    align: "center", // Keep the labels on the bars
                    color: "black",
                    font: {
                      weight: "bold",
                      size: 12,
                    },
                    rotation: -90, // Rotate the labels by 90 degrees
                    formatter: (value) => Math.round(value), // Remove decimals for sales
                  },
                },
                layout: {
                  padding: 10,
                },
              }}
            />
          </Box>

          {/* Waste Chart */}
          <Box
            sx={{
              width: "100%", // Each chart takes half of the width
              padding: "10px",
              height: "300px",
            }}
          ></Box>
        </>
      )}
      <Box
        sx={{
          width: "100%",
          padding: "10px",
          height: "400px", // Fixed height for the chart
        }}
      ></Box>
    </Box>
  );
}
