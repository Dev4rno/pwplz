let toastTimeout; // To store the timeout ID

function copyToClipboard(id, method) {
    const passwordField = document.getElementById(id);
    passwordField.select();
    document.execCommand("copy");
    showToast(method);
}

function showToast(method) {
    const toast = document.getElementById("toast");
    if (toastTimeout) {
        clearTimeout(toastTimeout);
    }
    // Update and show toast
    toast.textContent = `${method} password copied`;
    toast.classList.add("show");
    // Hide the toast
    toastTimeout = setTimeout(() => {
        toast.classList.remove("show");
    }, 1500);
}

// Reloader
document.getElementById("regenerateButton").addEventListener("click", () => {
    location.reload();
});
