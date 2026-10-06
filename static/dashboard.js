const airValues = [];
const timeLabels = [];

const alertHistory = [];

let previousAlert = false;


// --------------------------------
// Air quality score threshold
// --------------------------------

const POOR_SCORE_THRESHOLD = 65;


// --------------------------------
// Create graph
// --------------------------------

const ctx = document.getElementById("airChart");

const chart = new Chart(ctx, {

    type: "line",

    data: {

        labels: timeLabels,

        datasets: [

            {
                label: "Air Quality Score",

                data: airValues,

                borderWidth: 2,

                tension: 0.3
            },

            {
                label: "Poor Air Threshold",

                data: [],

                borderWidth: 1,

                borderDash: [6, 6],

                pointRadius: 0
            }

        ]

    },

    options: {

        responsive: true,

        animation: false,

        scales: {

            y: {
                beginAtZero: true,
                min: 0,
                max: 100,

                title: {
                    display: true,
                    text: "Air Quality Score"
                }
            },

            x: {
                title: {
                    display: true,
                    text: "Time"
                }
            }

        }

    }

});


// --------------------------------
// Update dashboard
// --------------------------------

function updateDashboard() {

    fetch("/data")

        .then(response => response.json())

        .then(data => {


            // --------------------------------
            // Air quality score
            // --------------------------------

            document.getElementById("air-quality").textContent =
                data.air_quality;


            // --------------------------------
            // Air quality status
            // --------------------------------

            document.getElementById("status").textContent =
                data.status;


            const indicator =
                document.getElementById("status-indicator");


            // GOOD and MODERATE do not trigger
            // the fan/buzzer in the firmware.

            if (
                data.status === "GOOD" ||
                data.status === "MODERATE"
            ) {

                indicator.className =
                    "status-indicator status-safe";

            }

            else {

                indicator.className =
                    "status-indicator status-poor";

            }


            // --------------------------------
            // Fan
            // --------------------------------

            document.getElementById("fan").textContent =
                data.fan ? "ON" : "OFF";


            const fanIndicator =
                document.getElementById("fan-indicator");


            if (data.fan) {

                fanIndicator.textContent =
                    "● Running";

                fanIndicator.className =
                    "device-status device-on";

            }

            else {

                fanIndicator.textContent =
                    "● Stopped";

                fanIndicator.className =
                    "device-status device-off";

            }


            // --------------------------------
            // Buzzer / alert
            // --------------------------------

            document.getElementById("alert").textContent =
                data.alert ? "ACTIVE" : "NORMAL";


            const buzzerIndicator =
                document.getElementById("buzzer-indicator");


            if (data.alert) {

                buzzerIndicator.textContent =
                    "● Alert Active";

                buzzerIndicator.className =
                    "device-status device-alert";

            }

            else {

                buzzerIndicator.textContent =
                    "● Normal";

                buzzerIndicator.className =
                    "device-status device-off";

            }


            // --------------------------------
            // Current time
            // --------------------------------

            const now =
                new Date();


            const timeString =
                now.toLocaleTimeString();


            const dateString =
                now.toLocaleDateString();


            document.getElementById("last-updated").textContent =
                timeString;


            // --------------------------------
            // Air quality history graph
            // --------------------------------

            timeLabels.push(timeString);

            airValues.push(data.air_quality);


            // Keep latest 20 readings

            if (timeLabels.length > 20) {

                timeLabels.shift();

                airValues.shift();

            }


            // Poor-air threshold line

            chart.data.datasets[1].data =
                timeLabels.map(() =>
                    POOR_SCORE_THRESHOLD
                );


            chart.update();


            // --------------------------------
            // Statistics
            // --------------------------------

            updateStatistics();


            // --------------------------------
            // Alert history
            // --------------------------------

            // Add an alert only when the system
            // changes from normal -> alert.

            if (data.alert && !previousAlert) {

                addAlertToHistory(
                    data.air_quality,
                    data.status,
                    timeString,
                    dateString
                );

            }


            previousAlert = data.alert;

        })


        .catch(error => {

            console.error(
                "Error getting dashboard data:",
                error
            );

        });

}


// --------------------------------
// Statistics
// --------------------------------

function updateStatistics() {

    if (airValues.length === 0) {
        return;
    }


    const minimum =
        Math.min(...airValues);


    const maximum =
        Math.max(...airValues);


    const total =
        airValues.reduce(
            (sum, value) => sum + value,
            0
        );


    const average =
        Math.round(
            total / airValues.length
        );


    document.getElementById("min-value").textContent =
        minimum;


    document.getElementById("average-value").textContent =
        average;


    document.getElementById("max-value").textContent =
        maximum;

}


// --------------------------------
// Add alert to history
// --------------------------------

function addAlertToHistory(
    airScore,
    status,
    time,
    date
) {

    alertHistory.push({

        airScore: airScore,

        status: status,

        time: time,

        date: date

    });


    document.getElementById("alert-count").textContent =
        alertHistory.length;


    const historyContainer =
        document.getElementById("alert-history");


    const noAlerts =
        document.getElementById("no-alerts");


    if (noAlerts) {
        noAlerts.remove();
    }


    const alertItem =
        document.createElement("div");


    alertItem.className =
        "alert-item";


    alertItem.innerHTML = `

        <div>

            <strong>
                ⚠ Air Quality Alert
            </strong>

            <p>
                ${status} — Air Quality Score: ${airScore}
            </p>

        </div>


        <span>

            ${date}<br>
            ${time}

        </span>

    `;


    historyContainer.prepend(alertItem);


    // Keep only the latest 10 visible alerts

    const items =
        historyContainer.querySelectorAll(
            ".alert-item"
        );


    if (items.length > 10) {

        items[items.length - 1].remove();

    }

}


// --------------------------------
// Clear alert history
// --------------------------------

document
    .getElementById("clear-history")
    .addEventListener("click", function() {


        alertHistory.length = 0;


        document.getElementById("alert-count").textContent =
            "0";


        const historyContainer =
            document.getElementById("alert-history");


        historyContainer.innerHTML = `

            <p id="no-alerts">
                No alerts recorded yet.
            </p>

        `;

    });


// --------------------------------
// Start dashboard
// --------------------------------

updateDashboard();


setInterval(
    updateDashboard,
    1000
);