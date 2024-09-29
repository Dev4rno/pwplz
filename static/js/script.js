let toastTimeout;

function copyToClipboard(id, method) {
    const passwordField = document.getElementById(id);
    passwordField.select();
    document.execCommand("copy");
    showToast(method);
}

function showToast(method) {
    const toast = document.getElementById("toast");
    if (toastTimeout) clearTimeout(toastTimeout);
    toast.textContent = `${method} password copied`;
    toast.classList.add("show");
    toastTimeout = setTimeout(() => {
        toast.classList.remove("show");
    }, 1500);
}

document.getElementById("regenerate-button").addEventListener("click", () => {
    location.reload();
});
