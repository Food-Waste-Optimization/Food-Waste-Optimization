import React, { useState, useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ChartDataLabels
);

export default function GraphSales({ mealDetails, restaurant }) {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cache, setCache] = useState({});

  const generateMealUrl = (date, mealIds) => {
    return `https://megasense-server.cs.helsinki.fi/fwowebserver/forecast/pos?restaurant=${restaurant}&date=${date}&meal_ids=${mealIds.join(
      ","
    )}`;
  };

  const fetchMealData = async (url) => {
    if (cache[url]) {
      return cache[url];
    }

    try {
      const response = await fetch(url);
      const data = await response.json();
      setCache((prevCache) => ({ ...prevCache, [url]: data.meals || [] }));
      return data.meals || [];
    } catch (error) {
      console.error("Error fetching meal data:", error);
      return [];
    }
  };

  useEffect(() => {
    const loadMealData = async () => {
      if (!mealDetails || mealDetails.length === 0) return;
      setLoading(true);
      let dateWiseMeals = {};
      const fetchPromises = [];

      for (const mealForDay of mealDetails) {
        const { date, meal_ids } = mealForDay;

        for (const [index, mealSet] of meal_ids.entries()) {
          const url = generateMealUrl(date, mealSet);
          fetchPromises.push(
            fetchMealData(url).then((fetchedMeals) => {
              const totalSales = fetchedMeals.reduce(
                (acc, meal) => acc + meal.pcs_pred,
                0
              );

              if (!dateWiseMeals[date]) {
                dateWiseMeals[date] = [];
              }
              dateWiseMeals[date].push({
                mealSetIndex: index,
                totalSales: Math.round(totalSales), // Round the totalSales here
              });
            })
          );
        }
      }

      await Promise.all(fetchPromises);

      // Sort the dates in ascending order (this is the key change)
      const sortedDates = Object.keys(dateWiseMeals).sort((a, b) => {
        return new Date(a) - new Date(b); // Sort by date
      });

      // Set the sorted chart data
      setChartData(
        sortedDates.map((date) => ({
          date,
          mealSets: dateWiseMeals[date],
        }))
      );
      setLoading(false);
    };
    loadMealData();
  }, [mealDetails, restaurant]);

  const getColorForSet = (index, numSets) => {
    const colorPalette = [
      "#A4D9B2", // Blue
      "#B3A6D3", // Red
      "#FFB870", // Yellow
    ];

    if (numSets === 3) {
      return colorPalette[index % 3]; // Always return one of the first 3 colors
    }

    if (numSets === 1) {
      return colorPalette[0]; // Use the first color for all
    }

    return colorPalette[index % colorPalette.length]; // Cycle through colors
  };

  const formatDate = (date) => {
    // Format the date as MM/DD
    const [year, month, day] = date.split("-");
    return `${month}/${day}`;
  };

  return (
    <Box sx={{ padding: "20px" }}>
      {loading ? (
        <CircularProgress
          sx={{
            color: "#155C2C",
            marginLeft: "30px",
            marginTop: "30px",
          }}
        />
      ) : (
        <>
          <Typography
            variant="h6"
            sx={{
              marginBottom: "-50px", // Reduced margin to bring the title closer to the graph
              textAlign: "center",
            }}
          >
            Weekly sales forecast per day
          </Typography>

          {/* Sales Bar Chart */}
          <Box sx={{ height: "340px", width: "100%" }}>
            <Bar
              data={{
                labels: chartData.flatMap((data) =>
                  data.mealSets.map(
                    (set, index) =>
                      `${formatDate(data.date)} (Option ${index + 1})`
                  )
                ),
                datasets: [
                  {
                    label: "Forecasted Sales",
                    data: chartData.flatMap((data) =>
                      data.mealSets.map((set) => set.totalSales)
                    ),
                    backgroundColor: chartData.flatMap((data) =>
                      data.mealSets.map(
                        (set, setIndex) =>
                          getColorForSet(setIndex, data.mealSets.length) // Pass mealSets length
                      )
                    ),
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: "top", display: false },
                  tooltip: { enabled: true },
                  datalabels: {
                    color: "#5a6268",
                    font: { size: 16, weight: "bold" },
                    rotation: -90,
                    align: "center",
                    anchor: "center",
                    padding: 5,
                    formatter: (value) => Math.round(value), // Round the value to the nearest whole number
                  },
                },
                scales: {
                  x: {
                    title: { display: true, text: "Date (Menu Option)" },
                    ticks: {
                      autoSkip: false,
                      // Removed rotation of x-axis labels
                    },
                  },
                  y: {
                    title: { display: true, text: "Total Sales" },
                    beginAtZero: true,
                  },
                },
              }}
            />
          </Box>
        </>
      )}
    </Box>
  );
}
