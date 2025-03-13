// Dark-/Light-Mode umschalten
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    setDarkModeIcon();
}

// Dark-Mode-Icon beim Laden der Seite setzen
function setDarkModeIcon() {
    let icon = document.getElementById("dark-light-toggle");
    if (document.body.classList.contains("dark-mode")) {
        icon.src = "static/images/light_mode.svg"; // Mond für Dark Mode
    } else {
        icon.src = "static/images/dark_mode.svg"; // Sonne für Light Mode
    }
}

// Steckbriefe standardmäßig eingeklappt halten
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".portfolio-details").forEach(detail => {
        detail.style.display = "none";
    });

    document.querySelectorAll(".portfolio-item").forEach(item => {
        item.classList.remove("expanded");
    });

    if (localStorage.getItem("dark-mode") === "enabled") {
        document.body.classList.add("dark-mode");
    }
    setDarkModeIcon();
});

// Steckbrief ausklappen/einklappen mit korrektem Layout
function toggleDetails(id) {
    var details = document.getElementById(id);
    var listItem = details.previousElementSibling;
    var icon = listItem.querySelector(".expand-icon");

    if (details.style.display === "none" || details.style.display === "") {
        details.style.display = "flex"; // "flex" sorgt dafür, dass das Bild rechts bleibt
        listItem.classList.add("expanded");
        icon.src = "static/images/collapse.svg"; // Ändert das Icon zum Pfeil-nach-oben
    } else {
        details.style.display = "none";
        listItem.classList.remove("expanded");
        icon.src = "static/images/expand.svg"; // Zurück zum Pfeil-nach-unten
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const profileIcon = document.getElementById("profileIcon");
    const dropdownMenu = document.getElementById("dropdownMenu");

    // Funktion zum Umschalten des Dropdown-Menüs
    profileIcon.addEventListener("click", function (event) {
        event.stopPropagation();  // Verhindert, dass der Klick das Dropdown schließt
        dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
    });

    // Schließe das Dropdown, wenn irgendwo anders auf der Seite geklickt wird
    document.addEventListener("click", function (event) {
        if (!profileIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = "none";
        }
    });
});
