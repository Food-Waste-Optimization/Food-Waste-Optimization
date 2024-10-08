import { Bar } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const BarCharts = ({ totalPieces, co2PerCustomer, wastePerCustomer }) => {
  const chartData = (color, dataValue) => ({
    labels: [""],
    datasets: [
      {
        label: "",
        data: [dataValue],
        backgroundColor: color,
      },
    ],
  });

  const chartOptions = (maxValue) => ({
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: false },
      legend: { display: false },
    },
    scales: {
      x: {
        beginAtZero: true,
        min: 0,
        max: maxValue,
        ticks: { color: "#000" },
      },
      y: {
        ticks: { display: false },
        grid: { display: false },
      },
    },
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-1 gap-2 py-0">
      <strong>
        <h3>Predicted total sold pieces</h3>
      </strong>
      <div
        className="bg-gray-100 shadow-md rounded-lg p-0"
        style={{ height: "150px", margin: "0px 0px 30px 0px" }}
      >
        <Bar
          data={chartData("#eeb291", totalPieces)}
          options={chartOptions(1000)}
        />
      </div>

      <strong>
        <h3>Predicted CO2 per customer (kg CO2e)</h3>
      </strong>
      <div
        className="bg-gray-100 shadow-md rounded-lg p-4"
        style={{ height: "150px", margin: "0px 0px 30px 0px" }}
      >
        <Bar
          data={chartData("#9dd4dd", co2PerCustomer)}
          options={chartOptions(1)}
        />
      </div>

      <strong>
        <h3>Predicted biowaste per customer (g)</h3>
      </strong>
      <div
        className="bg-gray-100 shadow-md rounded-lg p-4"
        style={{ height: "150px" }}
      >
        <Bar
          data={chartData("#b39ddb", wastePerCustomer * 1000)}
          options={chartOptions(100)}
        />
      </div>
    </div>
  );
};

export default BarCharts;
