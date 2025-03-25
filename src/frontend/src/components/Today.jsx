import React, { useState, useEffect } from "react";
import { Box, CircularProgress, Typography, Grid } from "@mui/material";
import { Bar, Pie } from "react-chartjs-2";
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

const locations = ["Chemicum", "Exactum", "Physicum", "Viikuna"];

const mealTypeColors = {
  vegan: "#6cc780", // Green
  vegetarian: "#fecd63", // Yellow
  chicken: "#FEA47F", // Red
  fish: "#75c6f5", // Blue
  meat: "#c49eff", // Purple
  default: "#A1E2D1", // Fallback color
};

const adjustColorShade = (baseColor, index) => {
  if (!baseColor) baseColor = mealTypeColors.default;
  const num = parseInt(baseColor.slice(1), 16);
  const variation = (index * 30) % 256;
  const r = (num >> 16) + variation;
  const g = ((num >> 8) & 0x00ff) + variation;
  const b = (num & 0x0000ff) + variation;

  return `#${(
    0x1000000 +
    (Math.min(255, Math.max(0, r)) << 16) +
    (Math.min(255, Math.max(0, g)) << 8) +
    Math.min(255, Math.max(0, b))
  )
    .toString(16)
    .slice(1)}`;
};

const preparePieChartData = (meals, key) => {
  return {
    labels: meals.map((meal) => meal.name),
    datasets: [
      {
        data: meals.map((meal) =>
          key === "sales" ? meal.pcs : meal[key] * meal.pcs
        ),
        backgroundColor: meals.map((meal, index) =>
          adjustColorShade(
            mealTypeColors[meal.meal_type] || mealTypeColors.default,
            index
          )
        ),
      },
    ],
  };
};

const prepareBarChartData = (meals, key) => {
  const roundedData = meals.map((meal) => {
    const value = key === "sales" ? meal.pcs : meal[key] * meal.pcs;
    return key === "sales" ? Math.round(value) : Math.round(value * 100) / 100;
  });

  return roundedData.reduce((acc, value) => acc + value, 0); // Sum the values after rounding
};

export default function Co2WasteChart() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const responses = await Promise.all(
          locations.map((location) =>
            fetch(
              `https://megasense-server.cs.helsinki.fi/fwowebserver/visualize?restaurant=${location}`
            )
          )
        );

        const results = await Promise.all(responses.map((res) => res.json()));

        const mealDataByLocation = locations.reduce((acc, loc, idx) => {
          acc[loc] = results[idx]?.meals || [];
          return acc;
        }, {});

        setData(mealDataByLocation);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
        setLoading(false);
      }
    };

    const formattedDate = new Date().toLocaleDateString("en-GB", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    setCurrentDate(formattedDate);
    fetchData();
  }, []);

  return (
    <Box sx={{ padding: "40px", boxSizing: "border-box" }}>
      <Typography variant="h5" sx={{ marginBottom: "20px" }}>
        <strong>Forecast for {currentDate}</strong>
      </Typography>

      <Box
        sx={{
          position: "sticky",
          top: "0",
          backgroundColor: "#fff",
          zIndex: 1,
          padding: "10px 0",
          marginBottom: "20px",
          boxShadow: "0 2px 2px rgba(0, 0, 0, 0.04)",
        }}
      >
        <Grid container spacing={4}>
          <Grid item sx={{ display: "flex", alignItems: "center" }}>
            <Box
              sx={{
                width: "20px",
                height: "20px",
                backgroundColor: "#FEA47F",
                marginLeft: "8px",
                marginRight: "8px",
              }}
            />
            <Typography variant="body2">Chicken</Typography>
          </Grid>
          <Grid item sx={{ display: "flex", alignItems: "center" }}>
            <Box
              sx={{
                width: "20px",
                height: "20px",
                backgroundColor: "#75c6f5",
                marginRight: "8px",
              }}
            />
            <Typography variant="body2">Fish</Typography>
          </Grid>
          <Grid item sx={{ display: "flex", alignItems: "center" }}>
            <Box
              sx={{
                width: "20px",
                height: "20px",
                backgroundColor: "#c49eff",
                marginRight: "8px",
              }}
            />
            <Typography variant="body2">Meat</Typography>
          </Grid>
          <Grid item sx={{ display: "flex", alignItems: "center" }}>
            <Box
              sx={{
                width: "20px",
                height: "20px",
                backgroundColor: "#6cc780",
                marginRight: "8px",
              }}
            />
            <Typography variant="body2">Vegan</Typography>
          </Grid>
          <Grid item sx={{ display: "flex", alignItems: "center" }}>
            <Box
              sx={{
                width: "20px",
                height: "20px",
                backgroundColor: "#fecd63",
                marginRight: "8px",
              }}
            />
            <Typography variant="body2">Vegetarian</Typography>
          </Grid>
        </Grid>
      </Box>

      {loading ? (
        <CircularProgress sx={{ color: "#155C2C", marginTop: "30px" }} />
      ) : (
        <>
          <Grid container spacing={4} justifyContent="center">
            {["sales", "waste", "co2"].map((key, idx) => (
              <Grid item xs={12} sm={4} key={idx}>
                <Box sx={chartContainerStyles}>
                  <Typography variant="h6">
                    {key === "sales"
                      ? "Total Customer Forecast"
                      : key === "waste"
                      ? "Total Waste Forecast (kg)"
                      : " Total CO₂ Forecast (kg CO₂e)"}
                  </Typography>
                  <Bar
                    data={{
                      labels: locations,
                      datasets: [
                        {
                          label:
                            key === "sales"
                              ? "Total Customers"
                              : key === "waste"
                              ? "Total Waste"
                              : "Total CO₂",
                          data: locations.map((loc) =>
                            prepareBarChartData(data[loc], key)
                          ),
                          backgroundColor: "#F7B7D1",
                        },
                      ],
                    }}
                    options={{
                      plugins: {
                        datalabels: {
                          formatter: (value) =>
                            key === "sales"
                              ? Math.round(value)
                              : Math.round(value * 100) / 100,
                          color: "#5a6268",
                          font: { size: 12, weight: "bold" },
                        },
                      },
                    }}
                  />
                </Box>
              </Grid>
            ))}
          </Grid>

          <Grid
            container
            spacing={4}
            justifyContent="center"
            sx={{ marginTop: "0px" }}
          >
            {locations.map((location) => (
              <React.Fragment key={location}>
                {["sales", "waste", "co2"].map((key, idx) => (
                  <Grid item xs={12} sm={4} key={`${location}-${key}`}>
                    <Box sx={chartContainerStyles}>
                      <Typography variant="h6">
                        {location} -{" "}
                        {key === "sales"
                          ? "Customer Forecast"
                          : key === "waste"
                          ? "Waste Forecast"
                          : "CO₂ Forecast (kg CO₂e)"}
                      </Typography>
                      <Pie
                        data={preparePieChartData(data[location], key)}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            tooltip: { enabled: true },
                            datalabels: {
                              color: "#5a6268",
                              font: { weight: "bold" },
                              formatter: (value) => {
                                return key === "sales"
                                  ? Math.round(value)
                                  : Math.round(value * 100) / 100;
                              },
                            },
                          },
                        }}
                      />
                    </Box>
                  </Grid>
                ))}
              </React.Fragment>
            ))}
          </Grid>
        </>
      )}
    </Box>
  );
}

const chartContainerStyles = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
  height: "400px",
  backgroundColor: "#fff",
  borderRadius: "10px",
  boxShadow: "0 20px 20px rgba(0, 0, 0, 0.04)",
  padding: "40px",
};
