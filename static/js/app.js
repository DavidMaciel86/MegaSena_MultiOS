/* ================================
   Histórico local (localStorage)
================================ */
const STORAGE_KEY = "megasurpresinhas_historico";

function getHistorico() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function salvarHistorico(item) {
  const historico = getHistorico();
  historico.unshift(item);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(historico));
}

function limparHistorico() {
  localStorage.removeItem(STORAGE_KEY);
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

