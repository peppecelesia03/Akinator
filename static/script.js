const startButton = document.querySelector("#startButton");
const answerButtons = document.querySelectorAll(".answer-button");
const statusText = document.querySelector("#statusText");
const questionText = document.querySelector("#questionText");

let currentQuestionId = null;

startButton.addEventListener("click", startGame);

answerButtons.forEach((button) => {
  button.addEventListener("click", () => {
    sendAnswer(button.dataset.answer);
  });
});

async function startGame() {
  setLoading(true);

  try {
    const response = await fetch("/api/start");
    const data = await parseResponse(response);
    renderStep(data);
  } catch (error) {
    renderError(error);
  } finally {
    setLoading(false);
  }
}

async function sendAnswer(answer) {
  if (!currentQuestionId) {
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/api/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        domanda: currentQuestionId,
        risposta: answer,
      }),
    });
    const data = await parseResponse(response);
    renderStep(data);
  } catch (error) {
    renderError(error);
  } finally {
    setLoading(false);
  }
}

async function parseResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Errore durante la richiesta");
  }

  return data;
}

function renderStep(data) {
  if (data.finished) {
    currentQuestionId = null;
    statusText.textContent = "Risultato";
    questionText.textContent = `Secondo me stai pensando a ${data.result}.`;
    startButton.textContent = "Ricomincia";
    setAnswersEnabled(false);
    return;
  }

  currentQuestionId = data.question_id;
  statusText.textContent = `Domanda ${data.progress.answered + 1} di ${
    data.progress.total
  }`;
  questionText.textContent = data.question_text;
  startButton.textContent = "Ricomincia";
  setAnswersEnabled(true);
}

function renderError(error) {
  statusText.textContent = "Errore";
  questionText.textContent = error.message;
  setAnswersEnabled(false);
}

function setLoading(isLoading) {
  startButton.disabled = isLoading;

  answerButtons.forEach((button) => {
    button.disabled = isLoading || !currentQuestionId;
  });
}

function setAnswersEnabled(enabled) {
  answerButtons.forEach((button) => {
    button.disabled = !enabled;
  });
}
