import React, { useState, useEffect } from "react";
import axios from "axios";
import RecGrid from "./RecGrid";

const FetchNames = ({
  mealDetails,
  numRows,
  numWeeks,
  restaurant,
  selectedDate,
}) => {
  const [mealIds, setMealIds] = useState(null);
  const [mealNames, setMealNames] = useState(null);
  const [error, setError] = useState("");

  const getMealIds = async () => {
    try {
      const response1 = await axios.get(
        `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${restaurant}&date=${selectedDate.format(
          "YYYY-MM-DD"
        )}&num_rows=${numRows}&num_weeks=${numWeeks}`
      );

      const allMealIds = Object.values(response1.data).flatMap((weeks) =>
        weeks.flatMap((week) => week.flatMap((day) => day.meal_ids))
      );

      if (allMealIds.length === 0) {
        setMealIds([]);
        setMealNames([]);
        setError("");
        return;
      }

      setMealIds(allMealIds);
      setError("");
    } catch (err) {
      console.error("Error fetching meal IDs:", err);
      setError("Error fetching recommendations.");
      setMealIds([]);
      setMealNames([]);
    }
  };

  const getMealNames = async () => {
    try {
      if (!mealIds || mealIds.length === 0) return;

      const mealIdQuery = mealIds.map((id) => `meal_id=${id}`).join("&");
      const response2 = await axios.get(
        `https://megasense-server.cs.helsinki.fi/fwowebserver/meal_info?restaurant=${restaurant}&${mealIdQuery}`
      );

      const mealMap = new Map();
      response2.data.forEach((meal) => {
        mealMap.set(meal.meal_id, meal.name);
      });

      const mealNamesFromApi = mealIds.map(
        (id) => mealMap.get(id) || `Meal ID ${id}`
      );

      setMealNames(mealNamesFromApi);
    } catch (err) {
      console.error("Error fetching meal names:", err);
      setError("Error fetching meal names.");
      setMealNames([]);
    }
  };

  useEffect(() => {
    setMealIds(null);
    setMealNames(null);
    setError("");
    getMealIds();
  }, [restaurant, selectedDate, numRows, numWeeks]);

  useEffect(() => {
    if (mealIds && mealIds.length > 0) {
      getMealNames();
    } else if (mealIds && mealIds.length === 0) {
      setMealNames([]);
    }
  }, [mealIds]);

  const isMealDetailsEmpty =
    !mealDetails || mealDetails.every((week) => !week || week.length === 0);

  return (
    <div style={{ minHeight: "80px" }}>
      {error ? (
        <div>{error}</div>
      ) : mealIds === null || mealNames === null ? null : isMealDetailsEmpty ||
        mealNames.length === 0 ? (
        <div style={{ padding: "16px", fontSize: "16px", color: "#555" }}>
          No recommendation for the selected options.
        </div>
      ) : (
        <RecGrid
          mealDetails={mealDetails}
          mealNames={mealNames}
          restaurant={restaurant}
          numRows={numRows}
        />
      )}
    </div>
  );
};

export default FetchNames;
