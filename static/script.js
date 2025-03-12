let toastTimeout;

// Clipboard handler
function copyToClipboard(id, method) {
    const passwordField = document.getElementById(id);
    passwordField.select();

    // Use the newer Clipboard API for better compatibility
    navigator.clipboard
        .writeText(passwordField.value)
        .then(() => {
            showToast(method);
        })
        .catch((err) => {
            console.error("Failed to copy: ", err);
        });
}

// Toast handler
function showToast(method) {
    const toast = document.getElementById("toast");
    if (toastTimeout) clearTimeout(toastTimeout);
    toast.textContent = `${method} password copied`;
    toast.classList.add("show");
    toastTimeout = setTimeout(() => {
        toast.classList.remove("show");
    }, 1500);
}
