function showSection(id) {
    document.querySelectorAll(".settings-section").forEach(s => s.classList.remove("active"));
    document.getElementById(id).classList.add("active");

    document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
    event.target.classList.add("active");
}
