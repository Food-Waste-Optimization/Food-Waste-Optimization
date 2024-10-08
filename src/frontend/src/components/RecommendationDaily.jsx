import { useState, useEffect } from "react";

import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { styled } from "@mui/material/styles";
import Tooltip from "@mui/material/Tooltip";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

import BarCharts from "./BarCharts.jsx";

const CustomTabs = styled(Tabs)({
  "& .MuiTabs-indicator": {
    backgroundColor: "#155C2C",
  },
});

const CustomTab = styled(Tab)({
  "&.Mui-selected": {
    color: "#155C2C",
  },
});

function RecommendationDaily() {
  const [selectedLocation, setSelectedLocation] = useState("Chemicum");
  const [selectedDate, setSelectedDate] = useState(null);
  const [menuData, setMenuData] = useState([]);
  const [rawData, setRawData] = useState(null);
  const [selectedMenu, setSelectedMenu] = useState(null);
  const [chartData, setChartData] = useState({
    totalPieces: 0,
    co2PerCustomer: 0,
    wastePerCustomer: 0,
  });
  const [dishes, setDishes] = useState([]);
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleLocationChange = (event) => {
    setSelectedLocation(event.target.value);
  };

  const handleDateChange = (newValue) => {
    setSelectedDate(newValue);
  };

  const fetchMenuData = async () => {
    if (!selectedDate) {
      alert("Please select a future date");
      return;
    }

    setLoading(true);
    const date = selectedDate.format("YYYY-MM-DD");
    const url = `https://megasense-server.cs.helsinki.fi/fwowebserver/recommendation?restaurant=${selectedLocation}&date=${date}`;

    try {
      const response = await fetch(url);
      const data = await response.json();
      console.log("Fetched Data:", data);

      setRawData(data);

      const filteredDishes = data.dishes_info.filter(
        (dish) => dish.restaurant === selectedLocation
      );
      setDishes(filteredDishes);

      const menusInfo = data.menus_info;

      const mappedMenus = menusInfo.map((menu) => {
        return {
          ...menu,
          dishes: [
            filteredDishes.find((dish) => dish.meal_id === menu.dish_1),
            filteredDishes.find((dish) => dish.meal_id === menu.dish_2),
            filteredDishes.find((dish) => dish.meal_id === menu.dish_3),
            filteredDishes.find((dish) => dish.meal_id === menu.dish_4),
          ],
        };
      });

      setMenuData(mappedMenus);
      if (mappedMenus.length > 0) {
        setSelectedMenu(mappedMenus[0]);
        setSelectedTabIndex(0);
      }
    } catch (error) {
      console.error("Error fetching menu data: ", error);
    } finally {
      setLoading(false);
    }
  };

  const handleMenuSelect = (menu) => {
    setSelectedMenu(menu);
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTabIndex(newValue);
    setSelectedMenu(menuData[newValue]);
  };

  const handleDishChange = (dishIndex, newDish) => {
    const updatedMenu = { ...selectedMenu };
    updatedMenu.dishes[dishIndex] = newDish;
    setSelectedMenu(updatedMenu);
  };

  const calculateChartData = (menu) => {
    if (!menu || !menu.dishes)
      return { totalPieces: 0, co2PerCustomer: 0, wastePerCustomer: 0 };

    const totalPieces = menu.dishes.reduce(
      (sum, dish) => sum + (dish ? dish.pcs_per_dish : 0),
      0
    );

    let totalCO2 = 0;
    let totalWaste = 0;

    menu.dishes.forEach((dish) => {
      if (dish) {
        const dishInfo = rawData.dishes_info.find(
          (item) => item.meal_id === dish.meal_id
        );

        if (dishInfo) {
          totalCO2 += dishInfo.co2 * dish.pcs_per_dish;
          totalWaste += dishInfo.waste * dish.pcs_per_dish;
        }
      }
    });

    const co2PerCustomer =
      totalPieces > 0 ? (totalCO2 / totalPieces).toFixed(2) : 0;
    const wastePerCustomer =
      totalPieces > 0 ? (totalWaste / totalPieces).toFixed(2) : 0;

    return {
      totalPieces,
      co2PerCustomer,
      wastePerCustomer,
    };
  };

  useEffect(() => {
    const newChartData = calculateChartData(selectedMenu);
    setChartData(newChartData);
  }, [selectedMenu]);

  const handleClick = () => {
    fetchMenuData();
  };

  return (
    <>
      <div className="w-full">
        <h1 className="text-4xl font-bold text-[#155C2C] px-2 pt-2">
          Daily Recommendation System
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
          <div className="bg-gray-100 shadow-lg rounded-lg p-6 flex-grow md:w-1/3 w-full">
            <div className="p-4">
              <h1 className="text-xl font-bold text-gray-800">
                Select location and date
              </h1>

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
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                  <DatePicker
                    value={selectedDate}
                    onChange={handleDateChange}
                    shouldDisableDate={(date) => {
                      const today = new Date();
                      const isPastDate = date.isBefore(today, "day");
                      const isWeekend = date.day() === 0 || date.day() === 6;
                      const isNextYear = date.isAfter("2024-12-31", "day");

                      return isPastDate || isWeekend || isNextYear;
                    }}
                  />
                </LocalizationProvider>
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
                Recommend daily menu
              </Button>

              {loading && (
                <div className="flex justify-center mt-4">
                  <CircularProgress sx={{ color: "#155C2C" }} />
                </div>
              )}
            </div>
          </div>

          <div className="bg-gray-100 shadow-lg rounded-lg p-6 flex-grow md:w-1/3 w-full">
            <div className="p-4">
              <h1 className="text-xl font-bold text-gray-800">
                Recommended menus
              </h1>

              <p className="mt-2 text-gray-600 py-3">
                Top 5 menus for your location and date, optimized by popularity,
                CO2 impact, and biowaste. You can customize the menus using the
                dropdowns, and the charts will update to reflect your changes.
              </p>

              <CustomTabs
                value={selectedTabIndex}
                onChange={handleTabChange}
                variant=""
                scrollButtons="auto"
                allowScrollButtonsMobile
              >
                {menuData.slice(0, 5).map((menu, index) => (
                  <CustomTab
                    style={{ minWidth: 60 }}
                    key={index}
                    label={`${index + 1}`}
                  />
                ))}
              </CustomTabs>

              <div className="mt-8 space-y-8">
                {selectedMenu &&
                  selectedMenu.dishes.map((dish, index) => (
                    <div className="grid grid-cols-10" key={index}>
                      <div
                        className="col-span-9"
                        style={{
                          backgroundColor: index < 2 ? "#d3e9bf" : "#f7eabe",
                          padding: "0px",
                          borderRadius: "4px",
                          marginBottom: "5px",
                          display: "flex",
                          alignItems: "center",
                        }}
                      >
                        <FormControl
                          fullWidth
                          variant="outlined"
                          sx={{
                            "& .MuiOutlinedInput-root": {
                              "& fieldset": {
                                borderWidth: "0px",
                              },
                              "&:hover fieldset": {
                                borderWidth: "0px",
                              },
                              "&.Mui-focused fieldset": {
                                borderWidth: "0px",
                              },
                            },
                            "& .MuiOutlinedInput-input": {
                              outline: "none",
                            },
                          }}
                          className="outline-none"
                        >
                          <Select
                            value={dish ? dish.meal_id : ""}
                            onChange={(e) =>
                              handleDishChange(
                                index,
                                dishes.find((d) => d.meal_id === e.target.value)
                              )
                            }
                            sx={{
                              boxShadow: "none",
                              ".MuiOutlinedInput-notchedOutline": { border: 0 },
                            }}
                          >
                            <MenuItem
                              disabled
                              style={{
                                fontWeight: "bold",
                                backgroundColor: "#f0f0f0",
                                textAlign: "center",
                              }}
                            >
                              Sorted by popularity
                            </MenuItem>

                            {index < 2
                              ? dishes
                                  .filter((d) => d.category === "vegan")
                                  .sort(
                                    (a, b) => b.pcs_per_dish - a.pcs_per_dish
                                  )
                                  .map((dishOption) => (
                                    <MenuItem
                                      key={dishOption.meal_id}
                                      value={dishOption.meal_id}
                                      style={{ padding: "15px 15px" }}
                                    >
                                      {dishOption.dish}
                                      <span
                                        className="ml-2"
                                        style={{ fontSize: "1.2rem" }}
                                      >
                                        {dishOption.category === "vegan" &&
                                          "🌱"}
                                        {dishOption.category === "fish" && "🐟"}
                                        {dishOption.category === "meat" && "🥩"}
                                        {dishOption.category === "chicken" &&
                                          "🍗"}
                                        {dishOption.category === "vegetarian" &&
                                          "🥗"}
                                      </span>
                                    </MenuItem>
                                  ))
                              : dishes
                                  .filter(
                                    (d) =>
                                      d.category === "chicken" ||
                                      d.category === "fish" ||
                                      d.category === "meat" ||
                                      d.category === "vegetarian"
                                  )
                                  .sort(
                                    (a, b) => b.pcs_per_dish - a.pcs_per_dish
                                  )
                                  .map((dishOption) => (
                                    <MenuItem
                                      key={dishOption.meal_id}
                                      value={dishOption.meal_id}
                                      style={{ padding: "15px 15px" }}
                                    >
                                      {dishOption.dish}
                                      <span
                                        className="ml-2"
                                        style={{ fontSize: "1.2rem" }}
                                      >
                                        {dishOption.category === "vegan" &&
                                          "🌱"}
                                        {dishOption.category === "fish" && "🐟"}
                                        {dishOption.category === "meat" && "🥩"}
                                        {dishOption.category === "chicken" &&
                                          "🍗"}
                                        {dishOption.category === "vegetarian" &&
                                          "🥗"}
                                      </span>
                                    </MenuItem>
                                  ))}
                          </Select>
                        </FormControl>
                      </div>

                      <Tooltip
                        title={
                          <div style={{ fontSize: "14px" }}>
                            <p>
                              Predicted sold pieces per dish:{" "}
                              {dish?.pcs_per_dish}
                            </p>
                            <p>Predicted CO2 per dish: {dish?.co2}</p>
                            <p>Predicted waste per dish: {dish?.waste}</p>
                          </div>
                        }
                        arrow
                        placement="top"
                      >
                        <div
                          style={{
                            marginLeft: "14px",
                            cursor: "pointer",
                            color: "#155C2C",
                          }}
                        >
                          info
                        </div>
                      </Tooltip>
                    </div>
                  ))}
              </div>
            </div>
          </div>

          <div className="bg-gray-100 shadow-lg rounded-lg p-6 flex-grow md:w-1/3 w-full">
            <div className="p-4">
              <BarCharts
                totalPieces={chartData.totalPieces}
                co2PerCustomer={chartData.co2PerCustomer}
                wastePerCustomer={chartData.wastePerCustomer}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default RecommendationDaily;
