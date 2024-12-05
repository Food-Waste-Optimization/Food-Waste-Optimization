import React, { useState, useEffect } from "react";
import axios from "axios";

import RecGrid from "./RecGrid";
import Graph from "./Graph";
import MealStats from "./MealStats";

const FetchNames = ({
  mealDetails,
  numRows,
  numWeeks,
  restaurant,
  selectedDate,
}) => {
  const [mealIds, setMealIds] = useState([]);
  const [mealNames, setMealNames] = useState([]);
  const [error, setError] = useState("");

  // Function to get meal IDs from the first API
  const getMealIds = async () => {
    try {
      const response1 = await axios.get(
        `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${restaurant}&date=${selectedDate}&num_rows=${numRows}&num_weeks=${numWeeks}`
      );
      console.log("Full response from first API:", response1.data);

      if (!response1.data || response1.data.length === 0) {
        throw new Error(
          "No meals found in the response or the array is empty."
        );
      }

      // Extract the meal_ids from each item in the response
      const allMealIds = response1.data.flatMap((item) => item.meal_ids); // Flatten meal_ids from each object in the array
      setMealIds(allMealIds); // Update state with the meal IDs
    } catch (error) {
      console.error("Error fetching meal IDs:", error);
      setError("Error fetching meal IDs.");
    }
  };

  // Function to get meal names based on the fetched meal IDs
  const getMealNames = async () => {
    try {
      if (mealIds.length === 0) {
        return;
      }

      // Ensure correct query format: meal_id=ID1&meal_id=ID2&meal_id=ID3...
      const mealIdQuery = mealIds.map((id) => `meal_id=${id}`).join("&");
      const response2 = await axios.get(
        `https://megasense-server.cs.helsinki.fi/fwowebserver/meal_info?restaurant=${restaurant}&${mealIdQuery}`
      );
      console.log("Response from second API:", response2.data); // Log the full response for debugging

      if (!response2.data || response2.data.length === 0) {
        throw new Error("No meal names found in the response.");
      }

      // Create a map of meal_id -> meal_name
      const mealMap = new Map();
      response2.data.forEach((meal) => {
        mealMap.set(meal.meal_id, meal.name);
      });

      // Map the meal names based on the meal IDs
      const mealNamesFromApi = mealIds.map((id) => {
        // If no name is found for a meal_id, show the meal_id itself
        return mealMap.has(id) ? mealMap.get(id) : `Meal ID ${id}`;
      });

      console.log("Mapped meal names:", mealNamesFromApi);
      setMealNames(mealNamesFromApi); // Update state with the meal names
    } catch (error) {
      console.error("Error fetching meal names:", error);
      setError("Error fetching meal names.");
    }
  };

  useEffect(() => {
    getMealIds(); // Call getMealIds when the component mounts
  }, [restaurant, selectedDate, numRows, numWeeks]);

  useEffect(() => {
    if (mealIds.length > 0) {
      getMealNames(); // Call getMealNames only when mealIds are populated
    }
  }, [mealIds]);

  return (
    <>
      <RecGrid
        mealDetails={mealDetails}
        mealNames={mealNames}
        restaurant={restaurant}
      />
      <MealStats
        mealDetails={mealDetails}
        mealNames={mealNames}
        restaurant={restaurant}
      />
    </>
  );
};

export default FetchNames;
