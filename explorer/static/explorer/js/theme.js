// Wait until the page is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("themeToggle");

    // If the button does not exist, stop the script
    if (!themeToggle) {
        return;
    }

    // Get saved theme from localStorage
    const savedTheme = localStorage.getItem("theme");

    // Apply saved theme
    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.textContent = "Light Mode";
    }

    // Toggle theme on click
    themeToggle.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");

        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
            themeToggle.textContent = "Light Mode";
        } else {
            localStorage.setItem("theme", "light");
            themeToggle.textContent = "Dark Mode";
        }
    });
});