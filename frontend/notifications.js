function showNotification(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'error') icon = '⚠️';
    if (type === 'success') icon = '✅';
    if (type === 'game') icon = '🎭';
    if (type === 'kill') icon = '🔪';
    
    toast.innerHTML = `<span class="toast-icon">${icon}</span> <span>${message}</span>`;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 4s
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Override window.alert to use our gamified notification automatically
window.alert = function(message) {
    let type = 'info';
    let lowerMsg = ("" + message).toLowerCase();
    if (lowerMsg.includes('error') || lowerMsg.includes('can\'t') || lowerMsg.includes('not a player') || lowerMsg.includes("must be") || lowerMsg.includes("not started")) {
        type = 'error';
    } else if (lowerMsg.includes('killed') || lowerMsg.includes('voted out') || lowerMsg.includes('game over')) {
        type = 'kill';
    } else if (lowerMsg.includes('started') || lowerMsg.includes('mafia')) {
        type = 'game';
    }
    showNotification(message, type);
};
