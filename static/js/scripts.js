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

function updateFileName(input) {
    const fileName = input.files.length > 0 ? input.files[0].name : "Keine Datei ausgewählt";
    document.getElementById("file-name").textContent = fileName;
}

let messages = [
    { text: "Willkommen im Chat!", category: "random", timestamp: "10:00", sender: "other" },
    { text: "Hat jemand neue Gaming-News?", category: "gaming", timestamp: "10:05", sender: "other" },
    { text: "Der neue AI-Artikel ist super!", category: "tech", timestamp: "10:10", sender: "other" },
];

function renderMessages(filter = "all") {
    fetch("/get_messages")
        .then(res => res.json())
        .then(data => {
            const chatBox = document.getElementById("chat-box");
            chatBox.innerHTML = "";

            data
                .filter(msg => filter === "all" || msg.category === filter)
                .reverse()
                .forEach(msg => {
                    const msgElement = document.createElement("div");
                    msgElement.classList.add("chat-message");
                    if (msg.username === document.getElementById("profileIcon")?.dataset.username) {
                        msgElement.classList.add("my-message");
                    }
                    msgElement.innerHTML = `<span class="timestamp">${msg.timestamp}</span> <strong>${msg.username}:</strong> ${msg.text}`;
                    chatBox.appendChild(msgElement);
                });
        });
}

function filterMessages() {
    const filter = document.getElementById("chat-filter").value;
    renderMessages(filter);
}

function sendMessage() {
    const input = document.getElementById("message-input");
    const text = input.value.trim();
    const category = document.getElementById("chat-filter").value;

    if (text !== "") {
        fetch("/send_message", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                text: text,
                category: category
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                input.value = "";
                filterMessages();  // neu rendern mit aktuellem Filter
            } else {
                alert(data.error);
            }
        });
    }
}


function confirmDelete(username) {
    const password = prompt("Bitte gib dein Admin-Passwort ein, um dieses Konto zu löschen:");
    if (password === null || password.trim() === "") return;

    fetch('/admin/delete_account', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Konto erfolgreich gelöscht. Du wirst jetzt ausgeloggt.");
            window.location.href = "/";
        } else {
            alert(data.message || "Löschen fehlgeschlagen.");
        }
    })
    .catch(err => {
        console.error("Fehler beim Löschen:", err);
        alert("Ein Fehler ist aufgetreten.");
    });
}


renderMessages();