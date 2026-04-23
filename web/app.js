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
  npcEffect: document.getElementById("npcEffect"),
  playerEffect: document.getElementById("playerEffect"),
  restartButton: document.getElementById("restartButton"),
  actionButtons: Array.from(document.querySelectorAll("[data-action]")),
};

const spriteSets = {
  player: {
    idle: ["/assets/player-idle-1.png", "/assets/player-idle-2.png"],
    advance: ["/assets/player-advance-1.png", "/assets/player-advance-2.png"],
    attack: ["/assets/player-attack-1.png", "/assets/player-attack-2.png"],
    guard: ["/assets/player-guard.png"],
    win: ["/assets/player-win-1.png", "/assets/player-win-2.png"],
    faint: ["/assets/player-faint.png"],
  },
  npc: {
    idle: ["/assets/npc-idle-1.png", "/assets/npc-idle-2.png"],
    advance: ["/assets/npc-advance-1.png", "/assets/npc-advance-2.png"],
    attack: ["/assets/npc-attack-1.png", "/assets/npc-attack-2.png"],
    guard: ["/assets/npc-guard.png"],
    win: ["/assets/npc-win-1.png", "/assets/npc-win-2.png"],
    faint: ["/assets/npc-faint.png"],
  },
};

const effectMap = {
  playerAttack: "/assets/effect-slash.png",
  playerGuard: "/assets/effect-guard.png",
  npcNormal: "/assets/effect-slash.png",
  npcStrong: "/assets/effect-impact.png",
  npcSpecial: "/assets/effect-pulse.png",
  npcGuard: "/assets/effect-guard.png",
  hit: "/assets/effect-hit.png",
};

let gameState = null;
let busy = false;
let idleTimer = null;
let animationLockUntil = 0;

function now() {
  return Date.now();
}

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

function spriteFor(side) {
  return side === "player" ? elements.playerSprite : elements.npcSprite;
}

function platformFor(side) {
  return spriteFor(side).parentElement;
}

function clearPlatformState(side) {
  platformFor(side).classList.remove("advance", "win", "faint");
}

function setSprite(side, src) {
  spriteFor(side).src = src;
}

function setIdleFrame(side, index = 0) {
  const frames = spriteSets[side].idle;
  setSprite(side, frames[index % frames.length]);
}

function startIdleLoop() {
  if (idleTimer) window.clearInterval(idleTimer);
  let frame = 0;
  idleTimer = window.setInterval(() => {
    if (now() < animationLockUntil) return;
    frame += 1;
    setIdleFrame("player", frame);
    setIdleFrame("npc", frame);
  }, 320);
}

function playSequence(side, frames, frameMs, options = {}) {
  const {
    delay = 0,
    holdLast = false,
    platformClass = null,
  } = options;

  const duration = delay + frames.length * frameMs + (holdLast ? frameMs : 0);
  animationLockUntil = Math.max(animationLockUntil, now() + duration);

  window.setTimeout(() => {
    if (platformClass) {
      clearPlatformState(side);
      platformFor(side).classList.add(platformClass);
    }

    frames.forEach((frame, index) => {
      window.setTimeout(() => {
        setSprite(side, frame);
      }, index * frameMs);
    });

    const restoreDelay = frames.length * frameMs + (holdLast ? frameMs : 0);
    window.setTimeout(() => {
      if (!holdLast) {
        clearPlatformState(side);
        setIdleFrame(side);
      }
    }, restoreDelay);
  }, delay);
}

function showEffect(target, src, delay = 0) {
  window.setTimeout(() => {
    target.classList.remove("visible");
    target.src = src;
    void target.offsetWidth;
    target.classList.add("visible");
    window.setTimeout(() => {
      target.classList.remove("visible");
    }, 420);
  }, delay);
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

function hpColor(value) {
  if (value <= 25) return "linear-gradient(90deg, #f07171 0%, #cb3f54 100%)";
  if (value <= 50) return "linear-gradient(90deg, #ffd56e 0%, #d89c39 100%)";
  return "linear-gradient(90deg, #83df7c 0%, #28b66f 100%)";
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

function renderState() {
  if (!gameState) return;

  updateBars();
  elements.turnText.textContent = gameState.terminado ? "Fin del combate" : `Turno ${gameState.turno}`;
  elements.distanceText.textContent = `Rango ${gameState.distancia} u`;
  elements.battleStatus.textContent = gameState.terminado
    ? (gameState.ganador === "Jugador" ? "Victoria" : "Derrota")
    : "Combate";

  setBusy(false);
}

function resetVisualState() {
  clearPlatformState("player");
  clearPlatformState("npc");
  elements.playerEffect.classList.remove("visible");
  elements.npcEffect.classList.remove("visible");
  animationLockUntil = 0;
  setIdleFrame("player", 0);
  setIdleFrame("npc", 0);
}

async function newGame() {
  setBusy(true);
  resetVisualState();

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
  startIdleLoop();
}

function animatePlayerAction(action) {
  if (action === "atacar") {
    playSequence("player", spriteSets.player.attack, 150);
    showEffect(elements.npcEffect, effectMap.playerAttack);
  } else if (action === "defender") {
    playSequence("player", spriteSets.player.guard, 260);
    showEffect(elements.playerEffect, effectMap.playerGuard);
  } else if (action === "acercarse") {
    playSequence("player", spriteSets.player.advance, 150, { platformClass: "advance" });
  } else if (action === "alejarse") {
    playSequence("player", spriteSets.player.advance.slice().reverse(), 150, { platformClass: "advance" });
  }
}

function animateNpcMove(move) {
  if (move === "Acercarse") {
    playSequence("npc", spriteSets.npc.advance, 150, { platformClass: "advance", delay: 90 });
  }
}

function animateNpcAttack(action) {
  if (!action || ["Huir", "Defender"].includes(action)) return;

  playSequence("npc", spriteSets.npc.attack, 150, { delay: 130 });
  if (action === "Ataque_Normal") showEffect(elements.playerEffect, effectMap.npcNormal, 80);
  if (action === "Ataque_Fuerte") showEffect(elements.playerEffect, effectMap.npcStrong, 80);
  if (action === "Ataque_Especial") showEffect(elements.playerEffect, effectMap.npcSpecial, 80);
}

function animateEndState(state) {
  if (!state.terminado) return;

  if (state.ganador === "Jugador") {
    playSequence("player", spriteSets.player.win, 180, { holdLast: true, platformClass: "win", delay: 180 });
    playSequence("npc", spriteSets.npc.faint, 260, { holdLast: true, platformClass: "faint", delay: 120 });
  } else {
    playSequence("npc", spriteSets.npc.win, 180, { holdLast: true, platformClass: "win", delay: 180 });
    playSequence("player", spriteSets.player.faint, 260, { holdLast: true, platformClass: "faint", delay: 120 });
  }
}

async function playTurn(action) {
  if (!gameState || gameState.terminado || busy) return;

  setBusy(true);

  const response = await fetch("/api/turno", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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

  animatePlayerAction(payload.jugador?.accion);
  animateNpcMove(payload.npc?.movimiento);

  if (payload.npc?.accion_ataque === "Defender") {
    playSequence("npc", spriteSets.npc.guard, 260, { delay: 100 });
    showEffect(elements.npcEffect, effectMap.npcGuard, 70);
  } else {
    animateNpcAttack(payload.npc?.accion_ataque);
  }

  if (payload.jugador?.danio > 0) {
    showEffect(elements.npcEffect, effectMap.hit, 140);
  }
  if ((payload.npc?.danio_aplicado ?? 0) > 0) {
    showEffect(elements.playerEffect, effectMap.hit, 180);
  }

  animateEndState(payload.estado);

  // Bloquear botones durante 2 segundos, luego actualizar estado
  window.setTimeout(() => {
    renderState();
  }, 1000);
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
