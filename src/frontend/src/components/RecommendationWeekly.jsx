import { useState } from "react";
import { useRef } from "react";

import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import CircularProgress from "@mui/material/CircularProgress";

import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers";

import { Line } from "react-chartjs-2";

import jsPDF from "jspdf";

function RecommendationWeekly() {
  const [selectedLocation, setSelectedLocation] = useState("Chemicum");
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedWeeks, setSelectedWeeks] = useState(1);
  const [loading, setLoading] = useState(false);
  const [totalPiecesPerDay, setTotalPiecesPerDay] = useState([]);
  const [TotalWaste, setTotalWaste] = useState([]);
  const [TotalCo2, setTotalCo2] = useState([]);

  const totalPiecesRef = useRef(null);
  const TotalWasteRef = useRef(null);
  const TotalCo2Ref = useRef(null);

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

    const totalPiecesArray = [];
    const TotalWasteArray = [];
    const TotalCo2Array = [];

    const labels = [];

    weeklyPlan.forEach((week) => {
      week.weekData.forEach((day) => {
        totalPiecesArray.push(day.totalPieces);
        TotalWasteArray.push(day.total_waste);
        TotalCo2Array.push(day.total_co2);

        labels.push(day.date.format("YYYY-MM-DD"));
      });
    });

    setTotalPiecesPerDay(totalPiecesArray);
    setTotalWaste(TotalWasteArray);
    setTotalCo2(TotalCo2Array);

    setChartLabels(labels);

    setTimeout(() => {
      generateWeeklyPlanPDF(weeklyPlan);
      setLoading(false);
    }, 1000); //wait for 1 second
  };

  const [chartLabels, setChartLabels] = useState([]);

  const fetchMenuDataForWeeks = async (startDate, location, weeks) => {
    const weeklyPlan = [];

    for (let i = 0; i < weeks; i++) {
      const weekData = [];

      //create an array to hold promises for fetching each day's data simultaneously

      const dailyPromises = [];

      for (let j = 0; j < 7; j++) {
        const currentDate = startDate.clone().add(i * 7 + j, "day");

        if (currentDate.day() >= 1 && currentDate.day() <= 5) {
          dailyPromises.push(
            (async () => {
              const menuData = await fetchMenuForDateAndLocation(
                currentDate,
                location
              );
              const totalPieces = await fetchTotalPiecesForDateAndLocation(
                currentDate,
                location
              );
              const TotalWaste = await fetchTotalWasteForDateAndLocation(
                currentDate,
                location
              );
              const TotalCo2 = await fetchTotalCo2ForDateAndLocation(
                currentDate,
                location
              );

              return {
                date: currentDate,
                menu: menuData,
                totalPieces,
                total_waste: TotalWaste,
                total_co2: TotalCo2,
              };
            })()
          );
        }
      }

      //wait for all promises to resolve
      const resolvedData = await Promise.all(dailyPromises);

      weekData.push(...resolvedData.filter((day) => day !== undefined));

      if (weekData.length > 0) {
        weeklyPlan.push({
          startDate: startDate.clone().add(i, "week"),
          weekData,
        });
      }
    }

    return weeklyPlan;
  };

  const fetchTotalPiecesForDateAndLocation = async (date, location) => {
    const formattedDate = date.format("YYYY-MM-DD");
    const url = `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${location}&date=${formattedDate}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      const menuInfo = data.menus_info[0];
      return menuInfo ? menuInfo.total_pcs_from_dishes || 0 : 0;
    } catch (error) {
      console.error("Error fetching total pieces:", error);
      return 0;
    }
  };

  const fetchTotalWasteForDateAndLocation = async (date, location) => {
    const formattedDate = date.format("YYYY-MM-DD");
    const url = `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${location}&date=${formattedDate}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      const menuInfo = data.menus_info[0];
      return menuInfo ? menuInfo.total_waste || 0 : 0;
    } catch (error) {
      console.error("Error fetching waste per customer:", error);
      return 0;
    }
  };

  const fetchTotalCo2ForDateAndLocation = async (date, location) => {
    const formattedDate = date.format("YYYY-MM-DD");
    const url = `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${location}&date=${formattedDate}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      const menuInfo = data.menus_info[0];
      return menuInfo ? menuInfo.total_co2 || 0 : 0;
    } catch (error) {
      console.error("Error fetching CO2 per customer:", error);
      return 0;
    }
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
    let chartImageHeight = 70;
    doc.text(
      `Weekly Menu Plan for ${selectedLocation} starting ${firstWeekStartDate}`,
      20,
      20
    );

    doc.setFontSize(14);

    let verticalOffset = 40;
    doc.setFontSize(12);

    const pageHeight = 300;

    weeklyPlan.forEach((week) => {
      const weekStart = week.startDate.format("YYYY-MM-DD");
      doc.setFontSize(14);
      doc.text(`Week starting ${weekStart}`, 20, verticalOffset);
      verticalOffset += 10;
      doc.setFontSize(12);

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

    doc.addPage();

    //capture charts as images and add to PDF

    doc.text("Predicted total sold pieces", 20, 40);
    if (totalPiecesRef.current) {
      const totalPiecesChartImage = totalPiecesRef.current.toBase64Image();
      doc.addImage(totalPiecesChartImage, "JPEG", 20, 30, 170, 70);
    }

    if (TotalWasteRef.current) {
      const TotalWasteChartImage = TotalWasteRef.current.toBase64Image();
      doc.addImage(TotalWasteChartImage, "JPEG", 20, 115, 170, 70);
    }
    doc.text("Predicted total waste", 20, 125);

    if (TotalCo2Ref.current) {
      const TotalCo2ChartImage = TotalCo2Ref.current.toBase64Image();
      doc.addImage(TotalCo2ChartImage, "JPEG", 20, 200, 170, 70);
    }
    doc.text("Predicted CO2", 20, 210);

    doc.save("weekly_menu_plan.pdf");
  };

  const data = {
    labels: chartLabels,
    datasets: [
      {
        label: "Total pieces",
        data: totalPiecesPerDay,
        fill: false,
        borderColor: "blue",
      },
      {
        label: "Waste per customer",
        data: TotalWaste,
        fill: false,
        borderColor: "green",
      },
      {
        label: "CO2 per customer",
        data: TotalCo2,
        fill: false,
        borderColor: "red",
      },
    ],
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

      <div className="mt-6">
        <div
          className="bg-gray-100 shadow-md rounded-lg p-4 w-1/2 mb-6"
          style={{
            height: "350px",
            margin: "0px 0px 30px 0px",
            visibility: "hidden",
            position: "absolute",
            left: "-9999px",
          }}
        >
          {totalPiecesPerDay.length > 0 && (
            <Line
              ref={totalPiecesRef}
              data={{
                labels: chartLabels,
                datasets: [
                  {
                    label: "Predicted total sold pieces",
                    data: totalPiecesPerDay,
                    borderColor: "#006400",
                    backgroundColor: "#8FBC8F",
                    dataPointColor: "#32CD32",
                    borderWidth: 2,
                  },
                ],
              }}
              options={{
                responsive: true,
                animation: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    suggestedMax: Math.max(...totalPiecesPerDay) + 100,
                  },
                },
              }}
            />
          )}
        </div>

        <div
          className="bg-gray-100 shadow-md rounded-lg p-4 w-1/2 mb-6"
          style={{
            height: "350px",
            margin: "0px 0px 30px 0px",
            visibility: "hidden",
            position: "absolute",
            left: "-9999px",
          }}
        >
          {TotalWaste.length > 0 && (
            <Line
              ref={TotalWasteRef}
              data={{
                labels: chartLabels,
                datasets: [
                  {
                    label: "Predicted total waste (kg)",
                    data: TotalWaste.map((value) => value),
                    borderColor: "#B22222",
                    backgroundColor: "#FF7F7F",
                    dataPointColor: "#FF0000",
                    borderWidth: 2,
                  },
                ],
              }}
              options={{
                responsive: true,
                animation: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    suggestedMax:
                      Math.max(...TotalWaste.map((value) => value)) + 10,
                  },
                },
              }}
            />
          )}
        </div>

        <div
          className="bg-gray-100 shadow-md rounded-lg p-4 w-1/2 mb-6"
          style={{
            height: "350px",
            margin: "0px 0px 30px 0px",
            visibility: "hidden",
            position: "absolute",
            left: "-9999px",
          }}
        >
          {TotalCo2.length > 0 && (
            <Line
              ref={TotalCo2Ref}
              data={{
                labels: chartLabels,
                datasets: [
                  {
                    label: "Predicted total CO2 (kg CO2e)",
                    data: TotalCo2,
                    borderColor: "#00008B",
                    backgroundColor: "#ADD8E6",
                    dataPointColor: "#1E90FF",
                    borderWidth: 2,
                  },
                ],
              }}
              options={{
                responsive: true,
                animation: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    suggestedMax: Math.max(...TotalCo2) + 0.2,
                  },
                },
              }}
            />
          )}
        </div>
      </div>
    </>
  );
}

export default RecommendationWeekly;
