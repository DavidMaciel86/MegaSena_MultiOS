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
    container.innerHTML =
      "<span class='small'>Nenhum histórico salvo neste dispositivo.</span>";
    return;
  }

  const jogoAtual = getJogoAtual();

  container.innerHTML = "";

  historico.forEach((item) => {
    const div = document.createElement("div");
    div.className = "historico-item";

    const jogosHtml = item.jogos.map((jogo, idx) => {
      // ===== Lotofácil: grade 5×N =====
      if (jogoAtual === "lotofacil") {
        const nums = jogo
          .map(
            (n) =>
              `<div class="lotofacil-num">${String(n).padStart(2, "0")}</div>`
          )
          .join("");

        return `
          <div style="margin-top:6px;">
            <b>${idx + 1})</b>
            <div class="lotofacil-grid">
              ${nums}
            </div>
          </div>
        `;
      }

      // ===== Mega-Sena (layout atual) =====
      return `
        <div>
          ${idx + 1}) ${jogo
            .map((n) => String(n).padStart(2, "0"))
            .join(" - ")}
        </div>
      `;
    }).join("");

    div.innerHTML = `
      <div><b>${item.data}</b></div>
      <div class="small">Modo: ${item.modo} | Fonte: ${item.fonte}</div>
      <div style="margin-top:6px;">
        ${jogosHtml}
      </div>
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