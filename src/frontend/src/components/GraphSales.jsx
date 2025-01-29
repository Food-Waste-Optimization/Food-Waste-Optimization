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

  const fetchMealData = async (url, signal) => {
    if (cache[url]) {
      return cache[url];
    }

    try {
      const response = await fetch(url, { signal });
      const data = await response.json();
      setCache((prevCache) => ({ ...prevCache, [url]: data.meals || [] }));
      return data.meals || [];
    } catch (error) {
      if (error.name !== "AbortError") {
        console.error("Error fetching meal data:", error);
      }
      return [];
    }
  };

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    const signal = controller.signal;

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
            fetchMealData(url, signal).then((fetchedMeals) => {
              if (!isMounted) return;

              const totalSales = fetchedMeals.reduce(
                (acc, meal) => acc + meal.pcs_pred,
                0
              );

              if (!dateWiseMeals[date]) {
                dateWiseMeals[date] = [];
              }
              dateWiseMeals[date].push({
                mealSetIndex: index,
                totalSales: Math.round(totalSales),
              });
            })
          );
        }
      }

      await Promise.all(fetchPromises);
      if (!isMounted) return;

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
      setLoading(false);
    };

    loadMealData();
    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [mealDetails, restaurant]);

  const getColorForSet = (index, numSets) => {
    const colorPalette = ["#A4D9B2", "#B3A6D3", "#FFB870"];
    return numSets === 3
      ? colorPalette[index % 3]
      : colorPalette[index % colorPalette.length];
  };

  const formatDate = (date) => {
    const [year, month, day] = date.split("-");
    return `${month}/${day}`;
  };

  return (
    <Box sx={{ padding: "20px" }}>
      {loading ? (
        <CircularProgress
          sx={{ color: "#155C2C", marginLeft: "30px", marginTop: "30px" }}
        />
      ) : (
        <>
          <Typography
            variant="h6"
            sx={{ marginBottom: "-50px", textAlign: "center" }}
          >
            Weekly customer forecast per day
          </Typography>
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
                    label: "Customers",
                    data: chartData.flatMap((data) =>
                      data.mealSets.map((set) => set.totalSales)
                    ),
                    backgroundColor: chartData.flatMap((data) =>
                      data.mealSets.map((set, setIndex) =>
                        getColorForSet(setIndex, data.mealSets.length)
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
                    font: { size: 12, weight: "bold" },
                    rotation: -90,
                    align: "center",
                    anchor: "center",
                    padding: 5,
                    formatter: (value) => Math.round(value),
                  },
                },
                scales: {
                  x: {
                    title: { display: true, text: "Date (Menu Option)" },
                    ticks: { autoSkip: false },
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
