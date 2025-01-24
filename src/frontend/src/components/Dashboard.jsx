import React, { useState, useEffect } from "react";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import CircularProgress from "@mui/material/CircularProgress";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { InputLabel } from "@mui/material";
import dayjs from "dayjs";

import FetchNames from "./FetchNames.jsx";

function Dashboard() {
  const [mealDetails, setMealDetails] = useState([]);
  const [labels, setLabels] = useState([]);
  const [totalPiecesArray, setTotalPiecesArray] = useState([]);
  const [totalWasteArray, setTotalWasteArray] = useState([]);
  const [totalCo2Array, setTotalCo2Array] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [restaurant, setRestaurant] = useState("Chemicum");
  const [selectedDate, setSelectedDate] = useState(null);
  const [numRows, setNumRows] = useState(1);
  const [numWeeks, setNumWeeks] = useState(1);
  const [showFetchNames, setShowFetchNames] = useState(false); // State to control visibility of FetchNames

  const getNextMonday = () => {
    const today = dayjs();
    const daysToNextMonday = (1 - today.day() + 7) % 7;
    return today.add(daysToNextMonday, "day").startOf("day");
  };

  useEffect(() => {
    const nextMonday = getNextMonday();
    setSelectedDate(nextMonday);
  }, []);

  const handleDateChange = (newValue) => {
    setSelectedDate(newValue);
    setShowFetchNames(false); // Hide FetchNames when any input is modified
  };

  const handleClick = () => {
    setIsLoading(true);
    setMealDetails([]);
    setLabels([]);
    setTotalPiecesArray([]);
    setTotalWasteArray([]);
    setTotalCo2Array([]);
    setShowFetchNames(true); // Show FetchNames after clicking recommend button

    const apiUrl = `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${restaurant}&date=${selectedDate}&num_rows=${numRows}&num_weeks=${numWeeks}`;

    fetch(apiUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch meal data");
        }
        return response.json();
      })
      .then((data) => {
        // Data processing (weeks-based)
        const structuredMealDetails = Object.keys(data).reduce(
          (acc, weekKey) => {
            const weekData = data[weekKey];

            // Process each week
            weekData.forEach((dailyMeals) => {
              dailyMeals.forEach((mealDay) => {
                const existingDay = acc.find(
                  (entry) => entry.date === mealDay.date
                );
                if (existingDay) {
                  existingDay.meal_ids.push(mealDay.meal_ids);
                } else {
                  acc.push({
                    date: mealDay.date,
                    meal_ids: [mealDay.meal_ids],
                  });
                }
              });
            });

            return acc;
          },
          []
        );

        setMealDetails(structuredMealDetails);
        setLabels(structuredMealDetails.map((entry) => entry.date));
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data from API:", error);
        setIsLoading(false);
      });
  };

  return (
    <>
      <div className="bg-white w-full rounded-lg p-8">
        <div className="flex justify-between items-center w-full gap-4">
          <FormControl
            variant="outlined"
            fullWidth
            sx={{
              flexBasis: "22%",
              "& .MuiOutlinedInput-root": {
                "& fieldset": {
                  borderColor: "#828282",
                  borderWidth: "1px",
                },
                "&:hover fieldset": {
                  borderColor: "#828282",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#000",
                  borderWidth: "1px",
                },
              },
            }}
          >
            <InputLabel
              sx={{
                backgroundColor: "#fff",
                paddingLeft: "4px",
                paddingRight: "4px",
              }}
            >
              Restaurant
            </InputLabel>
            <Select
              value={restaurant}
              onChange={(e) => {
                setRestaurant(e.target.value);
                setShowFetchNames(false);
              }}
            >
              <MenuItem value="Chemicum">
                <strong>Chemicum</strong>
              </MenuItem>
              <MenuItem value="Exactum">
                <strong>Exactum</strong>
              </MenuItem>
              <MenuItem value="Physicum">
                <strong>Physicum</strong>
              </MenuItem>
              <MenuItem value="Viikuna">
                <strong>Viikki</strong>
              </MenuItem>
            </Select>
          </FormControl>

          {/* Date Picker */}
          <FormControl
            variant="outlined"
            fullWidth
            sx={{
              flexBasis: "22%",
            }}
          >
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DatePicker
                value={selectedDate}
                onChange={handleDateChange}
                shouldDisableDate={(date) => {
                  const today = dayjs();
                  const isNotMonday = date.day() !== 1;

                  return isNotMonday;
                }}
                sx={{
                  "& .MuiInputBase-root": {
                    "& fieldset": {
                      borderColor: "#828282",
                      borderWidth: "1px",
                    },
                    "&:hover fieldset": {
                      borderColor: "#828282",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "#000",
                      borderWidth: "1px",
                    },
                  },
                }}
              />
            </LocalizationProvider>
          </FormControl>

          <FormControl
            variant="outlined"
            fullWidth
            sx={{
              flexBasis: "22%",
              "& .MuiOutlinedInput-root": {
                "& fieldset": {
                  borderColor: "#828282",
                  borderWidth: "1px",
                },
                "&:hover fieldset": {
                  borderColor: "#828282",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#000",
                  borderWidth: "1px",
                },
              },
            }}
          >
            <InputLabel
              sx={{
                backgroundColor: "#fff",
                paddingLeft: "4px",
                paddingRight: "4px",
              }}
            >
              Number of weeks
            </InputLabel>
            <Select
              value={numWeeks}
              onChange={(e) => {
                setNumWeeks(e.target.value);
                setShowFetchNames(false);
              }}
            >
              {[1, 2, 3, 4, 5, 6].map((week) => (
                <MenuItem key={week} value={week}>
                  {`${week} week${week > 1 ? "s" : ""}`}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl
            variant="outlined"
            fullWidth
            sx={{
              flexBasis: "22%",
              "& .MuiOutlinedInput-root": {
                "& fieldset": {
                  borderColor: "#828282",
                  borderWidth: "1px",
                },
                "&:hover fieldset": {
                  borderColor: "#828282",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#000",
                  borderWidth: "1px",
                },
              },
            }}
          >
            <InputLabel
              sx={{
                backgroundColor: "#fff",
                paddingLeft: "4px",
                paddingRight: "4px",
              }}
            >
              Number of options
            </InputLabel>
            <Select
              value={numRows}
              onChange={(e) => {
                setNumRows(e.target.value);
                setShowFetchNames(false);
              }}
            >
              {[1, 2, 3].map((menusperweek) => (
                <MenuItem key={menusperweek} value={menusperweek}>
                  {`${menusperweek} menu option${
                    menusperweek > 1 ? "s" : ""
                  } per week`}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            sx={{
              bgcolor: "#155C2C",
              "&:hover": { bgcolor: "#1C1C1C", color: "white" },
              maxWidth: "250px",
              width: "100%",
              whiteSpace: "nowrap",
              fontSize: { xs: "14px", sm: "16px", md: "18px" },
            }}
            size="medium"
            onClick={handleClick}
          >
            Recommend menu
          </Button>
        </div>

        <div className="bg-[#C8E6C9] shadow-lg rounded-lg px-2 w-full mt-4">
          {showFetchNames &&
            (isLoading ? (
              <CircularProgress
                sx={{
                  color: "#155C2C",
                  marginLeft: "30px",
                  marginTop: "30px",
                }}
              />
            ) : (
              <FetchNames
                mealDetails={mealDetails}
                labels={labels}
                restaurant={restaurant}
                numRows={numRows}
                numWeeks={numWeeks}
                selectedDate={selectedDate}
              />
            ))}
        </div>
      </div>
    </>
  );
}

export default Dashboard;
