// Grab all the specific HTML elements we need to interact with
const searchBtn = document.getElementById("search-btn");
const questionInput = document.getElementById("question-input");
const depthSelector = document.getElementById("depth-selector");
const errorBox = document.getElementById("error-box");
const loadingBox = document.getElementById("loading-box");
const progressText = document.getElementById("progress-text");
const resultsBox = document.getElementById("results-box");
const reportContent = document.getElementById("report-content");
const sourcesList = document.getElementById("sources-list");
const scoreDisplay = document.getElementById("score-display");
const roundsDisplay = document.getElementById("rounds-display");

// Listen for a click on the "Run Research" button
searchBtn.addEventListener("click", async () => {
    // Grab the text the user typed and the depth they selected
    const question = questionInput.value.trim();
    const depth = depthSelector.value;

    // Fast fail: Check if the prompt is too short before wasting AI API calls
    if (question.length < 10) {
        showError("Please enter a question with at least 10 characters.");
        return;
    }

    // Prepare the UI for loading: Hide old errors/results, show the loading box, and disable the button
    errorBox.classList.add("hidden");
    resultsBox.classList.add("hidden");
    loadingBox.classList.remove("hidden");
    searchBtn.disabled = true;

    // Start cycling through the progress labels (planning, searching, etc.)
    const progressTimer = startProgressLabels();

    try {
        // --- YOUR ESSENTIAL REQUEST ---
        const response = await fetch("/api/research", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, depth })
        });
        const data = await response.json();
        
        // If the server threw an error, trigger the catch block below
        if (!response.ok) throw new Error(data.detail || "Research failed");
        // ------------------------------

        // The AI succeeded! Stop the loading animation
        clearInterval(progressTimer);
        loadingBox.classList.add("hidden");

        // Fill in the Evidence Score and Search Rounds
        scoreDisplay.textContent = data.evidence_score;
        roundsDisplay.textContent = data.search_rounds;

        // Render the report. (Replacing \n with <br> ensures paragraph breaks show up correctly in HTML)
        reportContent.innerHTML = data.report.replace(/\n/g, "<br>");

        // Clear out any old source cards from a previous search
        sourcesList.innerHTML = "";
        
        // Loop through the list of sources the AI returned
        data.sources.forEach((source, index) => {
            // Create a new visual "card" for each source
            const card = document.createElement("div");
            card.className = "source-card";
            card.innerHTML = `
                <div class="source-title">[${index + 1}] ${source.title}</div>
                <a href="${source.url}" target="_blank" class="source-url">${source.url}</a>
            `;
            // Add the new card to the page
            sourcesList.appendChild(card);
        });

        // Make the final results visible to the user!
        resultsBox.classList.remove("hidden");

    } catch (err) {
        // If anything goes wrong, stop the loading animation and show our friendly error state
        clearInterval(progressTimer);
        loadingBox.classList.add("hidden");
        showError(err.message);
    } finally {
        // Whether it succeeded or failed, turn the button back on so the user can try again
        searchBtn.disabled = false;
    }
});

// Helper function: Unhides the error box and injects a custom message
function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
}

// Helper function: Cycles the loading text every 4 seconds to keep the user entertained
function startProgressLabels() {
    const labels = ["Planning strategy...", "Searching the web...", "Evaluating evidence...", "Writing final report..."];
    let currentIndex = 0;
    progressText.textContent = labels[0];
    
    return setInterval(() => {
        currentIndex = (currentIndex + 1) % labels.length;
        progressText.textContent = labels[currentIndex];
    }, 4000);
}