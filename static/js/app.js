/* ================================
   Histórico local (localStorage)
================================ */
function getJogoAtual() {
  const el = document.getElementById("historico-local");
  const jogo = el?.dataset?.jogo || "mega";
  return jogo;
}

function getStorageKey() {
  const jogo = getJogoAtual();
  return `megasurpresinhas_${jogo}_historico`;
}

function getHistorico() {
  try {
    return JSON.parse(localStorage.getItem(getStorageKey())) || [];
  } catch {
    return [];
  }
}

function salvarHistorico(item) {
  const historico = getHistorico();
  historico.unshift(item);
  localStorage.setItem(getStorageKey(), JSON.stringify(historico));
}

function limparHistorico() {
  localStorage.removeItem(getStorageKey());
}

function handleLimparHistorico() {
  const ok = confirm(
    "Tem certeza que deseja apagar todo o histórico gerado deste dispositivo?\n\nEssa ação não pode ser desfeita."
  );
  if (!ok) return;

  limparHistorico();
  renderHistorico();
  alert("Histórico limpo com sucesso.");
}

function renderHistorico() {
  const container = document.getElementById("historico-local");
  if (!container) return;

  const historico = getHistorico();

  if (!historico.length) {
    container.innerHTML = "<span class='small'>Nenhum histórico salvo neste dispositivo.</span>";
    return;
  }

  container.innerHTML = "";

  historico.forEach((item, idx) => {
    const div = document.createElement("div");
    div.className = "historico-item";

    const jogos = item.jogos
      .map(
        (j, i) =>
          `${i + 1}) ${j.map((n) => String(n).padStart(2, "0")).join(" - ")}`
      )
      .join("<br>");

    div.innerHTML = `
      <b>${item.data}</b><br>
      <span class="small">Modo: ${item.modo} | Fonte: ${item.fonte}</span><br>
      ${jogos}
    `;

    container.appendChild(div);
  });
}

/* ================================
   Tema (claro/escuro) com persistência
================================ */
const THEME_KEY = "megasurpresinhas_theme";

function applyTheme(theme) {
  const root = document.documentElement; // <html>
  root.setAttribute("data-theme", theme);

  const icon = document.getElementById("theme-icon");
  const label = document.getElementById("theme-label");

  if (theme === "dark") {
    if (icon) icon.textContent = "☀️";
    if (label) label.textContent = "Modo claro";
  } else {
    if (icon) icon.textContent = "🌙";
    if (label) label.textContent = "Modo escuro";
  }
}

function getSavedTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  return saved === "dark" ? "dark" : "light";
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
}

// Aplica tema ao abrir o app
document.addEventListener("DOMContentLoaded", () => {
  applyTheme(getSavedTheme());
});