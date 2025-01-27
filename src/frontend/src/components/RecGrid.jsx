import React, { useState, useEffect } from "react";
import {
  Box,
  Tabs,
  Tab,
  Pagination,
  Button,
  Menu,
  MenuItem,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import jsPDF from "jspdf";
import * as XLSX from "xlsx";
import { darken } from "@mui/system";
import GraphsStats from "./GraphsStats.jsx";
import GraphSales from "./GraphSales.jsx";

const CustomPagination = styled(Pagination)(({ theme, page }) => ({
  "& .MuiPaginationItem-root.Mui-selected": {
    backgroundColor:
      page === 1
        ? "#3C7A5A"
        : page === 2
        ? "#FF6347"
        : page === 3
        ? "#FFEB3B"
        : "#3C7A5A",
    color: "#fff",
    "&:hover": {
      backgroundColor:
        page === 1
          ? "#3C7A5A"
          : page === 2
          ? "#FF6347"
          : page === 3
          ? "#FFEB3B"
          : "#3C7A5A",
    },
  },
  "& .MuiPaginationItem-root": {
    color: "#555",
    "&:hover": {
      backgroundColor: "rgba(0, 0, 0, 0.1)",
    },
  },
}));

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

export default function RecGrid({
  mealDetails,
  mealNames,
  restaurant,
  numRows,
}) {
  const [selectedWeek, setSelectedWeek] = useState(0);
  const [paginationState, setPaginationState] = useState({});
  const [mealsData, setMealsData] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);

  const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const weekColors = ["#A4D9B2", "#C8BCE8", "#FFB870"];

  useEffect(() => {
    const fetchMealData = async () => {
      try {
        const response = await fetch(
          `https://megasense-server.cs.helsinki.fi/fwowebserver/meal_info?restaurant=${restaurant}`
        );
        const data = await response.json();
        setMealsData(data);
      } catch (error) {
        console.error("Error fetching meal data:", error);
      }
    };

    if (restaurant) {
      fetchMealData();
    }
  }, [restaurant]);

  const mealIdToNameMap = new Map();
  const mealKelaMap = new Map();
  const mealTypeMap = new Map();

  mealsData.forEach((meal) => {
    mealIdToNameMap.set(meal.meal_id, meal.name);
    mealKelaMap.set(meal.meal_id, meal.is_kela);
    mealTypeMap.set(meal.meal_id, meal.meal_type);
  });

  const weeks = [];
  for (let i = 0; i < mealDetails.length; i += 5) {
    weeks.push(mealDetails.slice(i, i + 5));
  }

  const weekData = weeks[selectedWeek];

  const handleTabChange = (event, newValue) => {
    setSelectedWeek(newValue);
  };

  const handlePaginationChange = (value) => {
    setPaginationState((prev) => ({
      ...prev,
      [selectedWeek]: value,
    }));
  };

  const getSelectedPageForWeek = () => {
    return paginationState[selectedWeek] || 1;
  };

  const resetOptions = () => {
    setPaginationState((prev) => {
      const resetState = { ...prev };
      Object.keys(resetState).forEach((weekIndex) => {
        resetState[weekIndex] = 1; // Reset each week to page 1
      });
      return resetState;
    });
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    const margin = 10;
    const pageHeight = doc.internal.pageSize.height;
    const pageWidth = doc.internal.pageSize.width;
    let currentY = 20;
    const mealsPerPage = 10;

    doc.setFontSize(16);
    doc.text(`Meal Plan for ${restaurant}`, margin, currentY);
    currentY += 10;

    weeks.forEach((week, weekIndex) => {
      doc.setFontSize(14);
      doc.text(`Week ${weekIndex + 1}`, margin, currentY);
      currentY += 10;

      const selectedOption = paginationState[weekIndex] || 1; // Get selected option for this week

      week.forEach((day, dayIndex) => {
        const yPos = currentY;

        const mealNamesList = (day.meal_ids[selectedOption - 1] || []).map(
          (mealId) => mealIdToNameMap.get(mealId) || "Unknown"
        );

        doc.setFontSize(12);
        doc.text(`${daysOfWeek[dayIndex]} (${day.date}):`, margin, currentY);
        currentY += 6;

        // Render meals for the day
        mealNamesList.forEach((mealName) => {
          if (currentY + 10 > pageHeight - margin) {
            doc.addPage();
            currentY = 20;
          }
          doc.text(mealName, margin, currentY);
          currentY += 6; // Space between meals
        });

        currentY += 10; // Space between days
      });

      currentY += 10; // Space between weeks
    });

    doc.save(`MealPlan_${restaurant}.pdf`);
  };

  const generateExcel = () => {
    const workbook = XLSX.utils.book_new();
    const sheetData = [];

    weeks.forEach((week, weekIndex) => {
      sheetData.push([`Week ${weekIndex + 1}`]);

      week.forEach((mealForDay, dayIndex) => {
        const { date, meal_ids } = mealForDay;
        const dayName = daysOfWeek[dayIndex];

        // Flatten the meal ids and map them to meal names
        const mealNames = meal_ids
          .flat()
          .map((id) => mealIdToNameMap.get(id) || "");

        // Add day data to the sheet
        sheetData.push([`${dayName} (${date})`, ...mealNames]);
      });

      sheetData.push([]); // Add an empty row after each week
    });

    const worksheet = XLSX.utils.aoa_to_sheet(sheetData);

    XLSX.utils.book_append_sheet(workbook, worksheet, "Meal Plan");

    XLSX.writeFile(workbook, `MealPlan_${restaurant}.xlsx`);
  };

  // Open menu to select file type
  const handleClickSave = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Close menu
  const handleClose = () => {
    setAnchorEl(null);
  };

  // PDF or Excel selection
  const handleMenuItemClick = (type) => {
    if (type === "pdf") {
      generatePDF();
    } else if (type === "excel") {
      generateExcel();
    }
    handleClose();
  };

  return (
    <div className="p-0 overflow-x-hidden">
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          padding: "20px 0px",
        }}
      >
        <Box
          sx={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: "15px",
            maxWidth: "65%",
            padding: "0px",
            borderRadius: "8px",
          }}
        >
          <Box
            sx={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              gap: "10px",
              maxWidth: "100%",
              padding: "10px",
              backgroundColor: "#f7f7f7",
              borderRadius: "8px",
            }}
          >
            {/* Week tabs, options, reset, save */}
            <Box
              sx={{
                display: "flex",
                flexWrap: "wrap", // Items wrap to next line if not enough space
                justifyContent: "space-between",
                alignItems: "center",
                gap: "10px",
                marginBottom: "10px",
                "@media (max-width: 900px)": {
                  flexDirection: "column",
                  alignItems: "stretch",
                },
              }}
            >
              <CustomTabs value={selectedWeek} onChange={handleTabChange}>
                {weeks.map((_, index) => (
                  <CustomTab key={index} label={`Week ${index + 1}`} />
                ))}
              </CustomTabs>

              <Box
                sx={{
                  display: "flex",
                  justifyContent: "flex-end",
                  alignItems: "center",
                  gap: "10px",
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    gap: 2,
                    justifyContent: "flex-start",
                    paddingTop: 0,
                  }}
                >
                  {Array.from({ length: numRows }, (_, index) => (
                    <Button
                      key={index}
                      onClick={() => handlePaginationChange(index + 1)}
                      variant=""
                      sx={{
                        padding: "6px 12px",
                        backgroundColor:
                          getSelectedPageForWeek() === index + 1
                            ? darken(weekColors[index % weekColors.length], 0.4)
                            : `${weekColors[index % weekColors.length]}80`,
                        color:
                          getSelectedPageForWeek() === index + 1
                            ? "#fff"
                            : "#000",
                        boxShadow:
                          getSelectedPageForWeek() === index + 1
                            ? "0 4px 8px rgba(0, 0, 0, 0.6)"
                            : "none",
                        "&:hover": {
                          backgroundColor:
                            getSelectedPageForWeek() === index + 1
                              ? darken(
                                  weekColors[index % weekColors.length],
                                  0.4
                                )
                              : `${weekColors[index % weekColors.length]}99`,

                          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
                        },
                        borderRadius: "16px",
                      }}
                    >
                      Option {index + 1}
                    </Button>
                  ))}
                </Box>
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={resetOptions}
                  sx={{
                    borderColor: "#3C7A5A",
                    color: "#3C7A5A",
                    "&:hover": {
                      backgroundColor: "#D3D3D3",
                      color: "#000",
                    },
                  }}
                >
                  Reset Options
                </Button>

                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleClickSave}
                  sx={{
                    backgroundColor: "#333333",
                    "&:hover": {
                      backgroundColor: "#000",
                    },
                  }}
                >
                  Save
                </Button>

                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleClose}
                >
                  <MenuItem onClick={() => handleMenuItemClick("pdf")}>
                    Save as PDF
                  </MenuItem>
                  <MenuItem onClick={() => handleMenuItemClick("excel")}>
                    Save as Excel
                  </MenuItem>
                </Menu>
              </Box>
            </Box>

            {/* Meals grid */}
            <Box
              sx={{
                display: "flex",
                gap: "10px",
                width: "100%",
                maxWidth: "100%",
                overflowX: "hidden",
                flexWrap: "nowrap",
                justifyContent: "space-between",
              }}
            >
              {weekData.map((mealForDay, dayIndex) => {
                return (
                  <Box
                    key={dayIndex}
                    sx={{
                      flex: "1 1 auto",
                      display: "flex",
                      flexDirection: "column",
                      width: "20%",
                      gap: "10px",
                      padding: "10px",
                      backgroundColor: "#f7f7f7",
                      borderRadius: "8px",
                      boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",

                      textAlign: "center",
                      width: "100%",
                    }}
                  >
                    <h3 style={{ fontWeight: "bold" }}>
                      {daysOfWeek[dayIndex]} ({mealForDay.date})
                    </h3>

                    {mealForDay.meal_ids[getSelectedPageForWeek() - 1]?.map(
                      (mealId) => {
                        const mealName = mealIdToNameMap.get(mealId) || "";
                        const isKela = mealKelaMap.get(mealId);
                        const mealType = mealTypeMap.get(mealId) || "";
                        const backgroundColor =
                          weekColors[getSelectedPageForWeek() - 1] || "#66BB6A";

                        return (
                          <Box
                            key={mealId}
                            sx={{
                              backgroundColor: backgroundColor,
                              padding: "10px",
                              borderRadius: "8px",
                              color: "black",
                            }}
                          >
                            <p
                              style={{
                                margin: 0,
                                textAlign: "left",
                                wordBreak: "break-word",
                                overflowWrap: "break-word",
                                hyphens: "auto",
                              }}
                            >
                              <span
                                style={{
                                  hyphens: "auto",
                                  wordBreak: "break-word",
                                  overflowWrap: "break-word",
                                }}
                              >
                                {mealName}
                              </span>{" "}
                              {isKela && (
                                <span
                                  style={{
                                    backgroundColor: "#FFD580",
                                    padding: "3px 5px",
                                    borderRadius: "4px",
                                    fontSize: "12px",
                                    whiteSpace: "nowrap",
                                  }}
                                >
                                  Kela
                                </span>
                              )}{" "}
                              {mealType && (
                                <span
                                  style={{
                                    backgroundColor: "#fff",
                                    padding: "3px 5px",
                                    borderRadius: "4px",
                                    fontSize: "12px",
                                    whiteSpace: "nowrap",
                                  }}
                                >
                                  {mealType}
                                </span>
                              )}
                            </p>
                          </Box>
                        );
                      }
                    )}
                  </Box>
                );
              })}
            </Box>
          </Box>
          {/* Graphs */}
          <Box
            sx={{
              backgroundColor: "#f7f7f7",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <GraphSales
              mealDetails={weeks[selectedWeek]}
              restaurant={restaurant}
            />
          </Box>
          <Box
            sx={{
              flex: 1,
              maxWidth: "70%",
              paddingTop: "20px",
              paddingLeft: "10px",
            }}
          >
            This recommendation system considers multiple factors, including
            popular meal choices, Kela requirements, a minimum number of vegan
            and fish meals per week, and biowaste and emissions targets.
          </Box>
        </Box>

        <Box sx={{ flex: 1, maxWidth: "35%" }}>
          <GraphsStats
            mealDetails={weeks[selectedWeek]}
            restaurant={restaurant}
          />
        </Box>
      </Box>
    </div>
  );
}
