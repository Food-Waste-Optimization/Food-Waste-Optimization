import React, { useState, useEffect } from "react";
import { Box, Tabs, Tab, Pagination, Button } from "@mui/material";
import { styled } from "@mui/material/styles";
import jsPDF from "jspdf";

const CustomPagination = styled(Pagination)(({ theme }) => ({
  "& .MuiPaginationItem-root.Mui-selected": {
    backgroundColor: "#3C7A5A",
    color: "#fff",
    "&:hover": {
      backgroundColor: "#3C7A5A",
    },
  },
  "& .MuiPaginationItem-root": {
    color: "#555",
    "&:hover": {
      backgroundColor: "rgba(0, 0, 0, 0.1)",
    },
  },
}));

export default function RecGrid({ mealDetails, mealNames, restaurant }) {
  const [selectedWeek, setSelectedWeek] = useState(0);
  const [paginationState, setPaginationState] = useState({});
  const [mealsData, setMealsData] = useState([]);

  const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

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

  // Flatten the meal details (this is done on mealDetails prop)
  const flattenedMealIds = mealDetails.reduce((acc, mealForDay) => {
    mealForDay.meal_ids.forEach((mealArray) => acc.push(...mealArray));
    return acc;
  }, []);

  // Create a map to associate mealId to mealName
  const mealIdToNameMap = new Map();
  mealsData.forEach((meal) => {
    mealIdToNameMap.set(meal.meal_id, meal.name);
  });

  // Create maps for Kela and mealType information
  const mealKelaMap = new Map();
  mealsData.forEach((meal) => {
    mealKelaMap.set(meal.meal_id, meal.is_kela);
  });

  const mealTypeMap = new Map();
  mealsData.forEach((meal) => {
    mealTypeMap.set(meal.meal_id, meal.meal_type);
  });

  // Group the meals into weeks for tab display
  const weeks = [];
  for (let i = 0; i < mealDetails.length; i += 5) {
    weeks.push(mealDetails.slice(i, i + 5));
  }

  const weekData = weeks[selectedWeek];

  const handleTabChange = (event, newValue) => {
    setSelectedWeek(newValue);
  };

  const handlePaginationChange = (dayIndex, value) => {
    const updatedPaginationState = { ...paginationState };
    if (!updatedPaginationState[selectedWeek]) {
      updatedPaginationState[selectedWeek] = Array(5).fill(1);
    }
    updatedPaginationState[selectedWeek][dayIndex] = value;
    setPaginationState(updatedPaginationState);
  };

  const resetPagination = () => {
    const resetState = {};
    weeks.forEach((week, weekIndex) => {
      resetState[weekIndex] = Array(5).fill(1);
    });
    setPaginationState(resetState);
  };

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

  const mealsPerPage = mealDetails
    .flatMap((day) => day.meal_ids)
    .reduce((max, mealArray) => Math.max(max, mealArray.length), 0);

  const generatePDF = () => {
    const doc = new jsPDF();
    let currentY = 20;
    const pageHeight = doc.internal.pageSize.height;

    const location = "Exactum";
    const selectedWeeksCount = weeks.length;

    const fileName = `MenuPlan_${location}_${selectedWeeksCount}weeks.pdf`;

    doc.setFontSize(20);
    doc.setFont("helvetica", "bold");
    doc.text(restaurant, 105, 15, { align: "center" });
    currentY += 10;

    weeks.forEach((week, weekIndex) => {
      doc.setFontSize(18);
      doc.text(`Week ${weekIndex + 1}`, 10, currentY);
      currentY += 10;

      week.forEach((mealForDay, dayIndex) => {
        const { date, meal_ids } = mealForDay;

        const currentPage = paginationState[weekIndex]?.[dayIndex] || 1;

        const flattenedMealIdsForDay = meal_ids.flat();
        const startIndex = (currentPage - 1) * mealsPerPage;
        const paginatedMeals = flattenedMealIdsForDay.slice(
          startIndex,
          startIndex + mealsPerPage
        );

        const dayName = daysOfWeek[dayIndex];
        doc.setFont("helvetica", "bold");
        doc.setFontSize(14);
        doc.text(`${dayName} (${date})`, 10, currentY);
        currentY += 10;

        doc.setFont("helvetica", "normal");

        paginatedMeals.forEach((id) => {
          const mealName = mealIdToNameMap.get(id) || `loading...`;

          doc.text(mealName, 10, currentY);
          currentY += 10;

          if (currentY + 10 > pageHeight) {
            doc.addPage();
            currentY = 20;
          }
        });

        currentY += 5;

        if (currentY + 20 > pageHeight) {
          doc.addPage();
          currentY = 20;
        }
      });

      currentY += 10;
    });

    doc.save(fileName);
  };

  return (
    <div className="p-0 overflow-x-hidden">
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "5px",
          padding: "20px 30px",
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
            gap: "10px",
          }}
        >
          <Button
            variant="outlined"
            sx={{
              color: "#155C2C",
              borderColor: "#155C2C",
              "&:hover": { bgcolor: "#f0f0f0", borderColor: "#1C1C1C" },
            }}
            onClick={resetPagination}
          >
            Reset Options
          </Button>
          <Button
            variant="contained"
            sx={{
              bgcolor: "#155C2C",
              "&:hover": { bgcolor: "#1C1C1C", color: "white" },
            }}
            onClick={generatePDF}
          >
            Save PDF
          </Button>
        </Box>
      </Box>

      {mealDetails.length === 0 ? (
        <p>No meal details available</p>
      ) : (
        <>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: "repeat(5, 1fr)", // 5 cards next to each other
              gap: "10px",
              marginLeft: "20px",
              marginRight: "20px",
              marginBottom: "30px",
              maxWidth: "100%",
            }}
          >
            {weekData.map((mealForDay, dayIndex) => {
              const { date, meal_ids } = mealForDay;
              const currentPage =
                paginationState[selectedWeek]?.[dayIndex] || 1;

              const flattenedMealIdsForDay = meal_ids.flat();
              const startIndex = (currentPage - 1) * mealsPerPage;
              const paginatedMeals = flattenedMealIdsForDay.slice(
                startIndex,
                startIndex + mealsPerPage
              );

              const totalPages = Math.ceil(
                flattenedMealIdsForDay.length / mealsPerPage
              );

              return (
                <Box
                  key={dayIndex}
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "flex-start",
                    backgroundColor: "#f7f7f7",
                    padding: "10px",
                    borderRadius: "8px",
                    boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
                    height: "auto",
                    maxWidth: "100%",
                    boxSizing: "border-box",
                    overflow: "hidden",
                    wordWrap: "break-word",
                    overflowWrap: "break-word",
                  }}
                >
                  <strong>{daysOfWeek[dayIndex]}</strong>
                  <p>{date}</p>

                  <Box sx={{ marginBottom: "10px" }}>
                    {totalPages > 1 && (
                      <CustomPagination
                        count={totalPages}
                        page={currentPage}
                        onChange={(e, value) =>
                          handlePaginationChange(dayIndex, value)
                        }
                      />
                    )}
                  </Box>

                  <div>
                    {paginatedMeals.map((mealId) => {
                      const mealName =
                        mealIdToNameMap.get(mealId) || `loading...`;

                      const isKela = mealKelaMap.get(mealId) ? " (Kela)" : "";
                      const mealType = mealTypeMap.get(mealId);

                      return (
                        <Box
                          key={mealId}
                          sx={{
                            backgroundColor: "#d1e7dd",
                            padding: "5px",
                            borderRadius: "4px",
                            marginTop: "5px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            flexWrap: "wrap",
                            wordWrap: "break-word",
                            overflowWrap: "break-word",
                          }}
                        >
                          <span>
                            {mealName}
                            <br />
                            {isKela && (
                              <span
                                style={{
                                  marginRight: "10px",
                                  backgroundColor: "#FFD580",
                                  padding: "3px 5px",
                                  borderRadius: "4px",
                                  fontSize: "0.9rem",
                                  color: "black",
                                }}
                              >
                                Kela
                              </span>
                            )}
                            {mealType && (
                              <span
                                style={{
                                  backgroundColor: "#FFB3A7",
                                  padding: "3px 5px",
                                  borderRadius: "4px",
                                  fontSize: "0.9rem",
                                }}
                              >
                                {mealType}
                              </span>
                            )}
                          </span>
                        </Box>
                      );
                    })}
                  </div>
                </Box>
              );
            })}
          </Box>
        </>
      )}
    </div>
  );
}
