// Processing JavaScript for real-time updates

function updateProcessingStatus(jobId) {
    fetch(`/api/processing/${jobId}`)
        .then(response => response.json())
        .then(data => {
            updateProgressBar(data);
            updateCounts(data);
            checkCompletion(data);
        })
        .catch(error => {
            console.error('Error updating status:', error);
        });
}

function updateProgressBar(data) {
    const processed = data.processed_count || 0;
    const total = data.total_providers || 1;
    const percentage = (processed / total) * 100;
    
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    if (progressBar) {
        progressBar.style.width = percentage + '%';
    }
    if (progressText) {
        progressText.textContent = `${processed} / ${total}`;
    }
}

function updateCounts(data) {
    const successCount = document.getElementById('successCount');
    const errorCount = document.getElementById('errorCount');
    const statusText = document.getElementById('statusText');
    
    if (successCount) {
        successCount.textContent = data.success_count || 0;
    }
    if (errorCount) {
        errorCount.textContent = data.error_count || 0;
    }
    if (statusText) {
        statusText.textContent = data.status || 'PENDING';
    }
}

function checkCompletion(data) {
    if (data.status === 'COMPLETED' || data.status === 'FAILED') {
        const completedStatus = document.getElementById('completedStatus');
        if (completedStatus) {
            completedStatus.classList.remove('hidden');
        }
    }
}

