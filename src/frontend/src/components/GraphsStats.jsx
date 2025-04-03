import React, { useState, useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { Bar, Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  RadialLinearScale,
} from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  RadialLinearScale,
  ChartDataLabels
);

export default function GraphsStats({ mealDetails, restaurant, selectedWeek }) {
  const [chartData, setChartData] = useState([]);
  const [radarData, setRadarData] = useState({ datasets: [] });
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
    let isMounted = true; // Prevents setting state if component unmounts
    const controller = new AbortController(); // Controls fetch cancellation
    const signal = controller.signal;

    const loadMealData = async () => {
      if (!mealDetails || mealDetails.length === 0) return;

      setLoading(true);
      let dateWiseMeals = {};
      let optionWiseMeals = {};
      let allMealSets = [];

      const fetchPromises = mealDetails.flatMap(({ date, meal_ids }) =>
        meal_ids.map(async (mealSet, index) => {
          const url = generateMealUrl(date, mealSet);

          try {
            const fetchedMeals = await fetchMealData(url, signal); // Pass the signal to cancel fetches

            if (!isMounted) return; // Prevents updating state if component unmounted

            const totalSales = fetchedMeals.reduce(
              (acc, meal) => acc + meal.pcs_pred,
              0
            );
            const totalCO2 = fetchedMeals.reduce(
              (acc, meal) => acc + meal.pcs_pred * meal.co2,
              0
            );
            const totalWaste = fetchedMeals.reduce(
              (acc, meal) => acc + meal.pcs_pred * meal.waste,
              0
            );
            const totalWasteHectograms = totalWaste * 10;

            if (!dateWiseMeals[date]) {
              dateWiseMeals[date] = [];
            }

            dateWiseMeals[date].push({
              mealSetIndex: index,
              totalSales,
              totalCO2,
              totalWasteHectograms,
            });

            if (!optionWiseMeals[index]) {
              optionWiseMeals[index] = {
                totalSales: 0,
                totalCO2: 0,
                totalWasteHectograms: 0,
              };
            }

            optionWiseMeals[index].totalSales += totalSales;
            optionWiseMeals[index].totalCO2 += totalCO2;
            optionWiseMeals[index].totalWasteHectograms += totalWasteHectograms;

            allMealSets.push({
              date,
              index,
              totalSales,
              totalCO2,
              totalWasteHectograms,
            });
          } catch (error) {
            if (error.name !== "AbortError") {
              console.error("Fetch error:", error);
            }
          }
        })
      );

      await Promise.all(fetchPromises);

      if (!isMounted) return; // Prevents setting state if the effect has been cleaned up

      const sortedDates = Object.keys(dateWiseMeals).sort(
        (a, b) => new Date(a) - new Date(b)
      );

      setChartData(
        sortedDates.map((date) => ({
          date,
          mealSets: dateWiseMeals[date].sort(
            (a, b) => a.mealSetIndex - b.mealSetIndex
          ),
        }))
      );

      setRadarData({
        labels: ["Waste", "CO2", "People"],
        datasets: Object.keys(optionWiseMeals)
          .map((optionIndex) => ({
            label: `Option ${parseInt(optionIndex) + 1}`,
            data: [
              optionWiseMeals[optionIndex].totalWasteHectograms,
              optionWiseMeals[optionIndex].totalCO2,
              Math.round(optionWiseMeals[optionIndex].totalSales),
            ],
            backgroundColor: getColorForSet(
              optionIndex,
              Object.keys(optionWiseMeals).length
            ),
            borderColor: getColorForSet(
              optionIndex,
              Object.keys(optionWiseMeals).length
            ),
            borderWidth: 2,
          }))
          .sort((a, b) => a.totalSales - b.totalSales),
      });

      setLoading(false);
    };

    loadMealData();

    return () => {
      isMounted = false; // Prevents updates on unmounted component
      controller.abort(); // Cancels any ongoing fetch requests
    };
  }, [mealDetails, restaurant, selectedWeek]);

  const getColorForSet = (index, numSets) => {
    const colorPalette = ["#A4D9B2", "#B3A6D3", "#FFB870"];

    if (numSets === 3) {
      return colorPalette[index % 3]; // Always return one of the 3 colours
    }

    if (numSets === 1) {
      return colorPalette[0]; // Use the first colour for all
    }

    return colorPalette[index % colorPalette.length]; // Cycle through colours
  };

  const formatDate = (date) => {
    // Format the date as MM/DD
    const [year, month, day] = date.split("-");
    return `${month}/${day}`;
  };

  return (
    <Box sx={{ paddingLeft: "14px" }}>
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
          {/* Radar Chart */}
          <Box
            sx={{
              width: "100%",
              height: "400px",
              marginBottom: "10px",
              backgroundColor: "#f7f7f7",
              borderRadius: "8px",
              boxShadow: "0 20px 20px rgba(0, 0, 0, 0.04)",
            }}
          >
            <Box sx={{ width: "100%", height: "110%" }}>
              <Radar
                data={radarData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                    datalabels: {
                      display: false,
                    },
                  },
                  scales: {
                    r: {
                      beginAtZero: true,
                      pointLabels: {
                        font: { size: 16 },
                      },
                      ticks: {
                        display: false,
                      },
                      grid: {
                        display: true,
                      },
                    },
                  },
                }}
              />
            </Box>
          </Box>

          {/* Waste Chart */}
          <Box
            sx={{
              width: "100%",
              height: "380px",
              marginBottom: "10px",
              backgroundColor: "#f7f7f7",
              borderRadius: "8px",
              padding: "18px",
              boxShadow: "0 20px 20px rgba(0, 0, 0, 0.04)",
            }}
          >
            <Typography
              variant="h6"
              sx={{ marginBottom: "-20px", textAlign: "center" }}
            >
              Waste per plate forecast for selected week (kg)
            </Typography>

            <Box sx={{ width: "100%", height: "350px" }}>
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
                      label: "Waste (kg)",
                      data: chartData.flatMap((data) =>
                        data.mealSets.map(
                          (set) =>
                            set.totalWasteHectograms / set.totalSales / 10
                        )
                      ),
                      backgroundColor: chartData.flatMap((data) =>
                        data.mealSets.map((_, index) => getColorForSet(index))
                      ),
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                    datalabels: {
                      color: "#5a6268",
                      font: { size: 12, weight: "bold" },
                      rotation: -90,
                      align: "center",
                      anchor: "center",
                      padding: 5,
                      formatter: (value) => value.toFixed(3),
                    },
                  },
                  scales: {
                    x: {
                      title: { display: true, text: "Date (Menu Option)" },
                      ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 20,
                      },
                    },
                    y: {
                      title: { display: true, text: "Total Waste (kg)" },
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </Box>
          </Box>

          {/* CO2 Chart */}
          <Box
            sx={{
              width: "100%",
              height: "380px",
              marginBottom: "10px",
              backgroundColor: "#f7f7f7",
              borderRadius: "8px",
              padding: "18px",
              boxShadow: "0 20px 20px rgba(0, 0, 0, 0.04)",
            }}
          >
            <Typography
              variant="h6"
              sx={{ marginBottom: "-20px", textAlign: "center" }}
            >
              Emissions per plate forecast for selected week (kg CO₂e)
            </Typography>

            <Box sx={{ width: "100%", height: "350px" }}>
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
                      label: "CO₂ emissions (kg CO₂e)",
                      data: chartData.flatMap((data) =>
                        data.mealSets.map(
                          (set) => set.totalCO2 / set.totalSales
                        )
                      ),
                      backgroundColor: chartData.flatMap((data) =>
                        data.mealSets.map((_, index) => getColorForSet(index))
                      ),
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                    datalabels: {
                      color: "#5a6268",
                      font: { size: 12, weight: "bold" },
                      rotation: -90,
                      align: "center",
                      anchor: "center",
                      padding: 5,
                      formatter: (value) => value.toFixed(3),
                    },
                  },
                  scales: {
                    x: {
                      title: {
                        display: true,
                        text: "Date (Menu Option)",
                      },
                      ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 20,
                      },
                    },
                    y: {
                      title: {
                        display: true,
                        text: "Total CO₂ Emissions (kg CO₂e)",
                      },
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </Box>
          </Box>
        </>
      )}
    </Box>
  );
}
