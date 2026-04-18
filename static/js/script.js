// Toast function
function showToast(message, type="error") {
    if (!message || message === "None") return; // 🔥 FIX

    const box = document.createElement("div");
    box.className = "toast-box";

    const toast = document.createElement("div");
    toast.className = "toast-msg " + (type === "error" ? "toast-error" : "toast-success");
    toast.innerText = message;

    box.appendChild(toast);
    document.body.appendChild(box);

    setTimeout(() => {
        box.remove();
    }, 3000);
}

// Trigger toast
document.addEventListener("DOMContentLoaded", () => {
    const msg = document.body.getAttribute("data-message");
    const type = document.body.getAttribute("data-type");

    showToast(msg, type);
});

// Button loading (clean)
document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
        const btn = form.querySelector("button");
        if (btn) {
            btn.innerHTML = "Processing...";
            btn.disabled = true;
        }
    });
});