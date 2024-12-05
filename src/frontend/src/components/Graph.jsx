import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2"; // Import Line graph from Chart.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register necessary Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Graph = () => {
  const [mealStats, setMealStats] = useState([]); // State to store meal stats fetched from the API
  const [loading, setLoading] = useState(true); // State to handle loading status
  const [error, setError] = useState(null); // State to handle errors

  // Fetch data from API on mount
  useEffect(() => {
    const fetchMealStats = async () => {
      try {
        console.log("Fetching data..."); // Log to ensure the fetch is being triggered

        const response = await fetch(
          "https://megasense-server.cs.helsinki.fi/fwowebserver/forecast/pos?restaurant=Exactum&date=2024-12-09&meal_ids=9049,7573,9500136,8991"
        );

        const rawData = await response.text(); // Fetch response as text to check raw data
        console.log("Raw API Response:", rawData); // Log the raw response for debugging

        // Manually replace any invalid characters (e.g., NaN) with valid values (e.g., 0)
        const cleanedData = rawData.replace(/NaN/g, "0"); // Replace NaN with 0 in the raw response
        console.log("Cleaned API Response:", cleanedData);

        // Now parse the cleaned JSON string
        const data = JSON.parse(cleanedData);

        // Validate the data structure
        if (data.meals && Array.isArray(data.meals)) {
          const sanitizedMeals = data.meals.map((meal) => ({
            ...meal,
            co2: isNaN(meal.co2) ? 0 : meal.co2, // Replace NaN with 0 for co2
            waste: isNaN(meal.waste) ? 0 : meal.waste, // Replace NaN with 0 for waste
            pcs: isNaN(meal.pcs) ? 0 : meal.pcs, // Replace NaN with 0 for pcs
          }));
          setMealStats(sanitizedMeals); // Update state with sanitized meals data
          console.log("Meal stats fetched successfully:", sanitizedMeals); // Log the sanitized meal stats
        } else {
          console.error("No valid meals data found in the response.");
          setError("No valid meals data found.");
        }
      } catch (error) {
        console.error("Error fetching meal stats:", error);
        setError("Error fetching data.");
      } finally {
        setLoading(false); // Set loading to false once data is fetched
      }
    };

    fetchMealStats();
  }, []); // Empty dependency array ensures this runs only once on mount

  // Debugging: Log data before rendering
  console.log("mealStats state:", mealStats);

  // Prepare chart data from fetched mealStats
  const chartData = {
    labels: mealStats.map((meal) => `Meal ${meal.meal_id}`), // Use meal_id as label
    datasets: [
      {
        label: "CO2 Emissions (kg)",
        data: mealStats.map((meal) => meal.co2), // CO2 values (already sanitized)
        borderColor: "rgba(75, 192, 192, 1)",
        fill: false,
        tension: 0.1,
      },
      {
        label: "Waste (kg)",
        data: mealStats.map((meal) => meal.waste), // Waste values (already sanitized)
        borderColor: "rgba(255, 99, 132, 1)",
        fill: false,
        tension: 0.1,
      },
      {
        label: "PCS",
        data: mealStats.map((meal) => meal.pcs), // PCS values (already sanitized)
        borderColor: "rgba(153, 102, 255, 1)",
        fill: false,
        tension: 0.1,
      },
    ],
  };

  // Chart options
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      tooltip: {
        mode: "index",
        intersect: false,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Meals", // X-axis label
        },
      },
      y: {
        title: {
          display: true,
          text: "Value", // Y-axis label
        },
      },
    },
  };

  return (
    <div>
      <h3>Meal Stats Graph</h3>
      {loading && <p>Loading data...</p>}{" "}
      {/* Show loading text until data is fetched */}
      {error && <p>{error}</p>} {/* Show error message if there is an issue */}
      {/* Debug: Display the raw API response data */}
      <h4>Raw API Response:</h4>
      <pre>{JSON.stringify(mealStats, null, 2)}</pre>
      {mealStats.length > 0 && (
        <div style={{ height: "400px", width: "100%" }}>
          {/* Render the Line chart with fetched data */}
          <Line data={chartData} options={options} />
        </div>
      )}
    </div>
  );
};

export default Graph;
