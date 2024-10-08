import { useState } from "react";

import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers";
import CircularProgress from "@mui/material/CircularProgress";

import jsPDF from "jspdf";

function RecommendationWeekly() {
  const [selectedLocation, setSelectedLocation] = useState("Chemicum");
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedWeeks, setSelectedWeeks] = useState(1);
  const [loading, setLoading] = useState(false);

  const handleLocationChange = (event) => {
    setSelectedLocation(event.target.value);
  };

  const handleDateChange = (newValue) => {
    setSelectedDate(newValue);
  };

  const handleWeeksChange = (event) => {
    setSelectedWeeks(event.target.value);
  };

  const handleClick = async () => {
    if (!selectedDate) {
      alert("Please select a future Monday");
      return;
    }

    const today = new Date();
    const isFutureMonday =
      selectedDate.isAfter(today, "day") && selectedDate.day() === 1;

    if (!isFutureMonday) {
      alert("Please select a future Monday");
      return;
    }

    setLoading(true);

    const startDate = selectedDate.startOf("week").add(1, "day");
    const location = selectedLocation;
    const weeklyPlan = await fetchMenuDataForWeeks(
      startDate,
      location,
      selectedWeeks
    );
    generateWeeklyPlanPDF(weeklyPlan);
    setLoading(false);
  };

  const fetchMenuDataForWeeks = async (startDate, location, weeks) => {
    let weeklyPlan = [];

    for (let i = 0; i < weeks; i++) {
      const weekData = [];
      for (let j = 0; j < 7; j++) {
        const currentDate = startDate.add(i * 7 + j, "day");
        const menuData = await fetchMenuForDateAndLocation(
          currentDate,
          location
        );
        if (
          menuData.length > 0 &&
          currentDate.day() !== 6 &&
          currentDate.day() !== 0
        ) {
          weekData.push({ date: currentDate, menu: menuData });
        }
      }
      if (weekData.length > 0) {
        weeklyPlan.push({ startDate: startDate.add(i, "week"), weekData });
      }
    }

    return weeklyPlan;
  };

  const fetchMenuForDateAndLocation = async (date, location) => {
    const formattedDate = date.format("YYYY-MM-DD");
    const url = `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${location}&date=${formattedDate}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      const menuInfo = data.menus_info[0];
      const dishes = menuInfo
        ? [
            menuInfo.dish_1,
            menuInfo.dish_2,
            menuInfo.dish_3,
            menuInfo.dish_4,
          ].map((dishId) => getDishDetailsById(dishId, data.dishes_info))
        : [];

      return dishes;
    } catch (error) {
      console.error("Error fetching menu data:", error);
      return ["No menu available"];
    }
  };

  const getDishDetailsById = (dishId, dishesInfo) => {
    const dish = dishesInfo.find((dish) => dish.meal_id === dishId);
    return dish
      ? { name: dish.dish, category: dish.category }
      : { name: "Unknown Dish", category: "" };
  };

  const generateWeeklyPlanPDF = (weeklyPlan) => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    const firstWeekStartDate = weeklyPlan[0].startDate.format("YYYY-MM-DD");
    doc.text(
      `Weekly Menu Plan for ${selectedLocation} starting ${firstWeekStartDate}`,
      20,
      20
    );
    doc.setFontSize(12);

    let verticalOffset = 40;
    const pageHeight = 300;

    weeklyPlan.forEach((week) => {
      const weekStart = week.startDate.format("YYYY-MM-DD");
      doc.setFontSize(14);
      doc.text(`Week starting ${weekStart}`, 20, verticalOffset);
      verticalOffset += 10;

      week.weekData.forEach((day) => {
        const dayName = day.date.format("dddd");
        const menuWithCategories = day.menu
          .map((dish) => `${dish.name} (${dish.category})`)
          .join(", ");

        if (verticalOffset + 20 > pageHeight) {
          doc.addPage();
          verticalOffset = 20;
        }

        doc.setFont("helvetica", "bold");
        doc.text(`${dayName}:`, 20, verticalOffset);
        verticalOffset += 10;

        doc.setFont("helvetica", "normal");
        const lines = doc.splitTextToSize(menuWithCategories, 180);

        lines.forEach((line) => {
          if (verticalOffset + 10 > pageHeight) {
            doc.addPage();
            verticalOffset = 20;
          }
          doc.text(line, 20, verticalOffset);
          verticalOffset += 10;
        });
      });

      verticalOffset += 10;
    });

    doc.save("weekly_menu_plan.pdf");
  };

  return (
    <>
      <div className="w-full">
        <h1 className="text-4xl font-bold text-[#155C2C] px-2 pt-2">
          Weekly Recommendation System
        </h1>
        <div className="flex items-end space-x-2 pt-2 justify-start">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="150"
            height="100"
            viewBox="-30 0 100 100"
            className="m-0"
          >
            <path
              d="M-20,50 C0,20, 30,20, 20,50 C10,80, -30,60, -20,50 Z"
              fill="#66BFA2"
            />
          </svg>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="120"
            height="100"
            viewBox="-30 0 100 100"
            className="m-0"
          >
            <path
              d="M-30,40 C-20,15, 20,15, 10,40 C0,65, -20,65, -30,40 Z"
              fill="#A3D9A5"
            />
          </svg>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="160"
            height="100"
            viewBox="-30 0 140 100"
            className="m-0"
          >
            <path
              d="M-30,30 C-20,5, 60,5, 40,30 C20,50, 0,70, -30,30 Z"
              fill="#C8E6C9"
            />
          </svg>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="120"
            height="100"
            viewBox="-30 0 100 100"
            className="m-0"
          >
            <path
              d="M-30,20 C-20,5, 10,5, 0,20 C-10,35, -30,30, -30,20 Z"
              fill="#D1E7DD"
            />
          </svg>
        </div>
      </div>

      <div className="bg-[#155C2C] w-full rounded-lg p-8">
        <div className="flex flex-col md:flex-row gap-6 justify-center items-start">
          <div className="bg-gray-100 shadow-lg rounded-lg p-6 w-full md:w-1/3 ">
            <div className="p-4">
              <h1 className="text-xl font-bold text-gray-800">
                Select location, date, and weeks
              </h1>
              <p className="mt-2 text-gray-600 py-3">
                A recommended menu plan will be available in PDF format after
                you complete the form. The plan is optimized by popularity, CO2
                impact, and biowaste.
              </p>
              <FormControl
                fullWidth
                variant="outlined"
                sx={{
                  marginTop: 2,
                  marginBottom: 2,
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                      borderColor: "#828282",
                      borderWidth: "1px",
                    },
                    "&:hover fieldset": {
                      borderColor: "#828282",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "#828282",
                      borderWidth: "1px",
                    },
                  },
                  "& .MuiOutlinedInput-input": {
                    outline: "none",
                  },
                }}
                className="outline-none"
              >
                <Select
                  value={selectedLocation}
                  onChange={handleLocationChange}
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
                </Select>
              </FormControl>

              <FormControl
                fullWidth
                variant="outlined"
                sx={{
                  marginBottom: 2,
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                      borderColor: "#828282",
                      borderWidth: "1px",
                    },
                    "&:hover fieldset": {
                      borderColor: "#828282",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "#828282",
                      borderWidth: "1px",
                    },
                  },
                  "& .MuiOutlinedInput-input": {
                    outline: "none",
                  },
                }}
                className="outline-none"
              >
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                  <DatePicker
                    value={selectedDate}
                    onChange={handleDateChange}
                    shouldDisableDate={(date) => {
                      const today = new Date();
                      const isPastDate = date.isBefore(today, "day");
                      const isNotMonday = date.day() !== 1;
                      const isNextYear = date.isAfter("2024-12-31", "day");
                      return isPastDate || isNotMonday || isNextYear;
                    }}
                  />
                </LocalizationProvider>
              </FormControl>

              <FormControl
                fullWidth
                variant="outlined"
                sx={{
                  marginBottom: 4,
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                      borderColor: "#828282",
                      borderWidth: "1px",
                    },
                    "&:hover fieldset": {
                      borderColor: "#828282",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "#828282",
                      borderWidth: "1px",
                    },
                  },
                  "& .MuiOutlinedInput-input": {
                    outline: "none",
                  },
                }}
                className="outline-none"
              >
                <Select value={selectedWeeks} onChange={handleWeeksChange}>
                  {[1, 2, 3, 4, 5].map((week) => (
                    <MenuItem key={week} value={week}>{`${week} week${
                      week > 1 ? "s" : ""
                    }`}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="contained"
                sx={{
                  bgcolor: "#155C2C",
                  "&:hover": { bgcolor: "#1C1C1C", color: "white" },
                }}
                size="large"
                onClick={handleClick}
              >
                Recommend weekly menu
              </Button>

              {loading && (
                <div className="flex justify-center items-center mt-4">
                  <CircularProgress sx={{ color: "#155C2C" }} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default RecommendationWeekly;
