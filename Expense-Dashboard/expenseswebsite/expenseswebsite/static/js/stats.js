const renderChart = (data, labels, type, canvasId, title) => {
  const ctx = document.getElementById(canvasId).getContext("2d");
  new Chart(ctx, {
    type: type,
    data: {
      labels: labels,
      datasets: [
        {
          label: `Last 6 months expenses (${type} view)`,
          data: data,
          backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(54, 162, 235, 0.2)",
            "rgba(255, 206, 86, 0.2)",
            "rgba(75, 192, 192, 0.2)",
            "rgba(153, 102, 255, 0.2)",
            "rgba(255, 159, 64, 0.2)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: title,
      },
    },
  });
};

const getChartData = () => {
  console.log("fetching");
  fetch("/expense_category_summary")
    .then((res) => res.json())
    .then((results) => {
      console.log("results", results);
      const category_data = results.expense_category_data;
      const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
      ];

      // Render Doughnut Chart
      renderChart(data, labels, "doughnut", "doughnutChart", "Expenses per category");

      // Render Bar Chart
      renderChart(data, labels, "bar", "barChart", "Expenses (Bar View)");

      // Render Pie Chart
      renderChart(data, labels, "pie", "pieChart", "Expenses (Pie View)");

      // Render Line Chart
      renderChart(data, labels, "line", "lineChart", "Expenses (Line View)");
    });
};

document.onload = getChartData();
