import React, { useState, useEffect } from "react";
import axios from "axios";

import RecGrid from "./RecGrid";
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
      console.log("Full response from first API:", response1.data); // Log the entire response for debugging

      if (!response1.data || Object.keys(response1.data).length === 0) {
        throw new Error(
          "No meals found in the response or the object is empty."
        );
      }

      // Flatten the structure of the meal IDs from the first API response
      const allMealIds = Object.values(response1.data).flatMap((weeks) =>
        weeks.flatMap(
          (week) => week.flatMap((day) => day.meal_ids) // Flatten all the meal_ids arrays
        )
      );

      if (allMealIds.length === 0) {
        throw new Error("No meal IDs found in the response.");
      }

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
        console.log("Mapping meal:", meal); // Log the meal being mapped
        mealMap.set(meal.meal_id, meal.name);
      });

      // Ensure that mealIds match up with names in the correct order
      const mealNamesFromApi = mealIds.map((id) => {
        if (mealMap.has(id)) {
          console.log(`Matched meal_id: ${id} -> ${mealMap.get(id)}`); // Log the match for debugging
          return mealMap.get(id);
        } else {
          console.log(`Meal ID ${id} not found in mealMap`); // Log any mismatches
          return `Meal ID ${id}`;
        }
      });

      console.log("Mapped meal names:", mealNamesFromApi);
      setMealNames(mealNamesFromApi); // Update state with the meal names
    } catch (error) {
      console.error("Error fetching meal names:", error);
      setError("Error fetching meal names.");
    }
  };

  useEffect(() => {
    getMealIds(); // Call getMealIds when the component mounts or dependencies change
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
