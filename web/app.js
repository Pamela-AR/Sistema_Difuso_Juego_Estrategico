const elements = {
  playerHealthBar: document.getElementById("playerHealthBar"),
  npcHealthBar: document.getElementById("npcHealthBar"),
  playerHealthText: document.getElementById("playerHealthText"),
  npcHealthText: document.getElementById("npcHealthText"),
  turnText: document.getElementById("turnText"),
  distanceText: document.getElementById("distanceText"),
  battleStatus: document.getElementById("battleStatus"),
  battleLog: document.getElementById("battleLog"),
  npcSprite: document.getElementById("npcSprite"),
  playerSprite: document.getElementById("playerSprite"),
  restartButton: document.getElementById("restartButton"),
  actionButtons: Array.from(document.querySelectorAll("[data-action]")),
};

let gameState = null;
let busy = false;
const animationDurations = {
  hit: 260,
  attack: 320,
  guard: 460,
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function setBusy(nextBusy) {
  busy = nextBusy;
  for (const button of elements.actionButtons) {
    button.disabled = nextBusy || gameState?.terminado;
  }
  elements.restartButton.disabled = nextBusy;
}

function renderLog(entries) {
  elements.battleLog.innerHTML = "";
  const items = entries && entries.length
    ? entries.slice(-3)
    : ["Una Bestia Difusa aparece frente a ti."];

  for (const entry of items) {
    const li = document.createElement("li");
    li.textContent = entry;
    elements.battleLog.appendChild(li);
  }
}

function animateSprite(sprite, className) {
  sprite.classList.remove("hit", "attack", "guard");
  void sprite.offsetWidth;
  sprite.classList.add(className);
  window.setTimeout(() => {
    sprite.classList.remove(className);
  }, animationDurations[className] ?? 320);
}

function updateBars() {
  const playerLife = clamp(gameState.vida_jugador, 0, 100);
  const npcLife = clamp(gameState.vida_npc, 0, 100);
  elements.playerHealthBar.style.width = `${playerLife}%`;
  elements.npcHealthBar.style.width = `${npcLife}%`;
  elements.playerHealthBar.style.background = hpColor(playerLife);
  elements.npcHealthBar.style.background = hpColor(npcLife);
  elements.playerHealthText.textContent = `${playerLife} / 100`;
  elements.npcHealthText.textContent = `${npcLife} / 100`;
}

function hpColor(value) {
  if (value <= 25) return "linear-gradient(90deg, #f07171 0%, #cb3f54 100%)";
  if (value <= 50) return "linear-gradient(90deg, #ffd56e 0%, #d89c39 100%)";
  return "linear-gradient(90deg, #83df7c 0%, #28b66f 100%)";
}

function renderState() {
  if (!gameState) return;

  updateBars();
  elements.turnText.textContent = gameState.terminado
    ? "Fin del combate"
    : `Turno ${gameState.turno}`;
  elements.distanceText.textContent = `Rango ${gameState.distancia} u`;

  if (gameState.terminado) {
    elements.battleStatus.textContent =
      gameState.ganador === "Jugador" ? "Victoria" : "Derrota";
  } else {
    elements.battleStatus.textContent = "En combate";
  }

  setBusy(false);
}

async function newGame() {
  setBusy(true);
  elements.playerSprite.classList.remove("hit", "attack", "guard");
  elements.npcSprite.classList.remove("hit", "attack", "guard");

  const response = await fetch("/api/estado");
  if (!response.ok) {
    throw new Error("No se pudo cargar el estado inicial.");
  }
  const payload = await response.json();

  gameState = payload.estado;
  renderLog([
    "Una Bestia Difusa aparece frente a ti.",
    "El combate comienza.",
  ]);
  renderState();
}

async function playTurn(action) {
  if (!gameState || gameState.terminado || busy) return;

  setBusy(true);

  const response = await fetch("/api/turno", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      estado: gameState,
      accion: action,
    }),
  });

  if (!response.ok) {
    const payload = await response.json();
    renderLog([payload.error || "No se pudo procesar el turno."]);
    setBusy(false);
    return;
  }

  const payload = await response.json();

  gameState = payload.estado;
  renderLog(payload.registro);
  renderState();

  const playerAction = payload.jugador?.accion;
  const npcAction = payload.npc?.accion_ataque;

  if (playerAction === "atacar") animateSprite(elements.playerSprite, "attack");
  if (playerAction === "defender") animateSprite(elements.playerSprite, "guard");
  if (npcAction && !["Huir", "Defender"].includes(npcAction)) {
    animateSprite(elements.npcSprite, "attack");
  }
  if (payload.jugador?.danio > 0) animateSprite(elements.npcSprite, "hit");
  if ((payload.npc?.danio_aplicado ?? 0) > 0) animateSprite(elements.playerSprite, "hit");
}

for (const button of elements.actionButtons) {
  button.addEventListener("click", () => playTurn(button.dataset.action));
}

elements.restartButton.addEventListener("click", () => {
  newGame().catch((error) => {
    console.error(error);
    renderLog(["No fue posible reiniciar la partida."]);
    setBusy(false);
  });
});

newGame().catch((error) => {
  console.error(error);
  renderLog(["No fue posible inicializar la arena."]);
  setBusy(false);
});
