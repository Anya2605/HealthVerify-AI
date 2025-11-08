// Chart.js configurations

function createValidationChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Validated', 'Partial', 'Flagged'],
            datasets: [{
                data: [
                    data.validated || 0,
                    data.partial || 0,
                    data.flagged || 0
                ],
                backgroundColor: [
                    '#10B981',
                    '#F59E0B',
                    '#EF4444'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

function createConfidenceChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['NPI', 'Address', 'Phone', 'Website'],
            datasets: [{
                label: 'Validation Rate (%)',
                data: [
                    data.npi_validation_rate || 0,
                    data.address_validation_rate || 0,
                    data.phone_validation_rate || 0,
                    0 // Website validation rate
                ],
                backgroundColor: '#3B82F6'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

