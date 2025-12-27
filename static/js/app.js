function formatJogosHTML(jogos) {
  if (!Array.isArray(jogos) || jogos.length === 0) return "";

  return `
    <div class="resultado-lista">
      ${jogos.map((jogo, idx) => {
        const dezenas = (Array.isArray(jogo) ? jogo : [])
          .map(n => String(n).padStart(2, "0"))
          .join(" - ");

        const numero = idx + 1;

        const quebra = (numero % 3 === 0 && numero !== jogos.length)
          ? `<div class="quebra-grupo"></div>`
          : "";

        return `
          <div class="linha-jogo">${numero}) ${dezenas}</div>
          ${quebra}
        `;
      }).join("")}
    </div>
  `;
}

function renderHistorico() {
  const container = document.getElementById("historico-local");
  if (!container) return;

  const historico = getHistorico();
  container.innerHTML = "";

  if (!Array.isArray(historico) || historico.length === 0) {
    container.innerHTML =
      `<div class="small">Nenhum histórico salvo neste dispositivo.</div>`;
    return;
  }

  historico.forEach((item, index) => {
    const div = document.createElement("div");
    div.style.margin = "10px 0";

    const meta = `${item.data || ""} — ${item.modo || ""} / ${item.fonte || ""}`;
    const jogosHTML = formatJogosHTML(item.jogos || []);

    div.innerHTML = `
      <span class="pill">${index + 1}</span>
      <span class="small">${meta}</span>
      ${jogosHTML}
    `;

    container.appendChild(div);
  });
}
