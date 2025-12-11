// QUIZ DATA
const quizzes = {
    philosophy: [
        { q: "Who said 'I think, therefore I am'?", options: ["Plato", "Aristotle", "Descartes", "Nietzsche"], answer: 2 },
        { q: "What is the study of existence?", options: ["Ethics", "Metaphysics", "Epistemology", "Logic"], answer: 1 },
        { q: "Who wrote 'The Republic'?", options: ["Socrates", "Plato", "Kant", "Hegel"], answer: 1 },
        { q: "Stoicism originated in which country?", options: ["Greece", "Rome", "Egypt", "Persia"], answer: 0 },
        { q: "What is the study of knowledge?", options: ["Epistemology", "Aesthetics", "Ethics", "Logic"], answer: 0 }
    ],
    literature: [
        { q: "Who wrote '1984'?", options: ["Orwell", "Huxley", "Bradbury", "Tolkien"], answer: 0 },
        { q: "Shakespeare wrote…", options: ["The Odyssey", "Hamlet", "Inferno", "Ulysses"], answer: 1 },
        { q: "Author of 'The Hobbit'?", options: ["Rowling", "Lewis", "Tolkien", "Adams"], answer: 2 },
        { q: "What is a haiku?", options: ["Novel", "Poem", "Drama", "Epic"], answer: 1 },
        { q: "Who wrote 'Pride and Prejudice'?", options: ["Bronte", "Austen", "Dickens", "Shelley"], answer: 1 }
    ],
    history: [
        { q: "The Roman Empire fell in…", options: ["476 AD", "800 AD", "1200 AD", "1492 AD"], answer: 0 },
        { q: "Who discovered America?", options: ["Vikings", "Columbus", "Magellan", "Da Gama"], answer: 1 },
        { q: "The Great Wall is in…", options: ["India", "Japan", "China", "Korea"], answer: 2 },
        { q: "Cold War was between…", options: ["US & USSR", "France & Germany", "China & Japan", "UK & Spain"], answer: 0 },
        { q: "Pyramids belong to…", options: ["Greece", "Egypt", "Rome", "Persia"], answer: 1 }
    ],
    science: [
        { q: "H2O is…", options: ["Hydrogen", "Oxygen", "Water", "Salt"], answer: 2 },
        { q: "Red Planet?", options: ["Mars", "Venus", "Jupiter", "Mercury"], answer: 0 },
        { q: "Speed of light?", options: ["300 km/s", "300,000 km/s", "150,000 km/s", "1,000 km/s"], answer: 1 },
        { q: "We breathe…", options: ["CO₂", "O₂", "N₂", "He"], answer: 1 },
        { q: "Earth revolves around…", options: ["Moon", "Mars", "Sun", "Stars"], answer: 2 }
    ],
    computer: [
        { q: "CPU stands for…", options: ["Core Power Unit", "Central Processing Unit", "Computer Program Utility", "Control Panel User"], answer: 1 },
        { q: "HTML is for…", options: ["Styling", "Logic", "Structure", "Databases"], answer: 2 },
        { q: "Python is…", options: ["Snake", "Language", "OS", "Chip"], answer: 1 },
        { q: "RAM is…", options: ["Storage", "Short-term memory", "CPU", "GPU"], answer: 1 },
        { q: "First computer virus year?", options: ["1969", "1986", "1999", "2008"], answer: 1 }
    ],
};

// QUIZ LOGIC
let currentQuiz = [];
let index = 0;
let score = 0;
let selectedAnswer = -1;
let quizTitle = "";

function startQuiz(id) {
    currentQuiz = quizzes[id];
    quizTitle = id.toUpperCase();

    index = 0;
    score = 0;

    document.getElementById("quizSelection").style.display = "none";
    document.getElementById("quizContainer").style.display = "block";
    document.getElementById("results").style.display = "none";

    loadQuestion();
}

function loadQuestion() {
    let q = currentQuiz[index];

    document.getElementById("questionNumber").innerText = `Question ${index + 1} of ${currentQuiz.length}`;
    document.getElementById("questionText").innerText = q.q;

    let html = "";
    q.options.forEach((opt, i) => {
        html += `<button class="option-btn" onclick="selectOption(${i})">${opt}</button>`;
    });

    document.getElementById("optionsContainer").innerHTML = html;
    selectedAnswer = -1;

    document.getElementById("progressFill").style.width =
        (index / currentQuiz.length) * 100 + "%";
}

function selectOption(i) {
    selectedAnswer = i;

    document.querySelectorAll(".option-btn").forEach(btn => btn.classList.remove("selected"));
    event.target.classList.add("selected");
}

function nextQuestion() {
    if (selectedAnswer === -1) {
        alert("Select an answer first!");
        return;
    }

    if (selectedAnswer === currentQuiz[index].answer) score++;

    index++;

    if (index >= currentQuiz.length) return showResults();
    loadQuestion();
}

function showResults() {
    document.getElementById("quizContainer").style.display = "none";
    document.getElementById("results").style.display = "block";

    document.getElementById("quizTitle").innerText = quizTitle;
    document.getElementById("scoreDisplay").innerText = `You scored ${score} / ${currentQuiz.length}`;

    let percent = (score / currentQuiz.length) * 100;

    document.getElementById("scoreMessage").innerText =
        percent >= 60 ? "Great job! 🎉" : "Keep practicing!";

    document.getElementById("pointsEarned").innerText =
        `You earned ${score} points! (Not saved to DB yet)`;
}

function backToSelection() {
    document.getElementById("quizSelection").style.display = "block";
    document.getElementById("quizContainer").style.display = "none";
    document.getElementById("results").style.display = "none";
}
