document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('date-range-form');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      
      const startDate = document.getElementById('start_date').value;
      const endDate = document.getElementById('end_date').value;
  
      fetch(`/weather-plot?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            alert(data.error);
            return;
          }
  
          if (data.dates && data.temps) {
            const dates = data.dates;
            const temps = data.temps;
  
            const ctx = document.createElement('canvas');
            document.getElementById('weather-plot-container').innerHTML = '';
            document.getElementById('weather-plot-container').appendChild(ctx);
  
            new Chart(ctx, {
              type: 'line',
              data: {
                labels: dates,
                datasets: [{
                  label: 'Average Temperature (°C)',
                  data: temps,
                  borderColor: 'rgba(75, 192, 192, 1)',
                  backgroundColor: 'rgba(75, 192, 192, 0.2)',
                  borderWidth: 1
                }]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  x: {
                    type: 'time',
                    time: {
                      unit: 'day'
                    },
                    title: {
                      display: true,
                      text: 'Date'
                    }
                  },
                  y: {
                    title: {
                      display: true,
                      text: 'Temperature (°C)'
                    }
                  }
                }
              }
            });
          } else {
            console.error("Invalid data format:", data);
          }
        })
        .catch(error => console.error('Error:', error));
    });
  });
  