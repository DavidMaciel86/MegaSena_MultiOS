/* ================================
   PWA - Service Worker
================================ */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", async () => {
    try {
      const reg = await navigator.serviceWorker.register("/sw.js");
      console.log("✅ Service Worker registrado com escopo:", reg.scope);
    } catch (err) {
      console.error("❌ Falha ao registrar o Service Worker:", err);
    }
  });
}

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

function renderHistorico() {
  const container = document.getElementById("historico-local");
  if (!container) return;

  const historico = getHistorico();
  container.innerHTML = "";

  if (historico.length === 0) {
    container.innerHTML =
      `<div class="small">Nenhum histórico salvo neste dispositivo.</div>`;
    return;
  }

  historico.forEach((item, index) => {
    const div = document.createElement("div");
    div.style.margin = "6px 0";
    div.innerHTML = `
      <span class="pill">${index + 1}</span>
      <span class="small">
        ${item.data} — ${item.modo} / ${item.fonte}
      </span>
      <div class="small" style="margin-top:6px;">
        ${item.jogos
          .map((jogo, i) =>
            `${i + 1}) ${jogo.map(n => String(n).padStart(2, "0")).join(" · ")}`
          )
          .join("<br>")}
      </div>

    `;
    container.appendChild(div);
  });
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

document.addEventListener("DOMContentLoaded", () => {
  renderHistorico();
});

/* ================================
   PWA - Aviso de atualização
================================ */
let newWorker;

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    window.location.reload();
  });

  navigator.serviceWorker.ready.then((reg) => {
    if (reg.waiting) {
      showUpdateBanner(reg.waiting);
    }

    reg.addEventListener("updatefound", () => {
      newWorker = reg.installing;
      newWorker.addEventListener("statechange", () => {
        if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
          showUpdateBanner(newWorker);
        }
      });
    });
  });
}

function showUpdateBanner(worker) {
  if (document.getElementById("update-banner")) return;

  const banner = document.createElement("div");
  banner.id = "update-banner";
  banner.style.position = "fixed";
  banner.style.bottom = "16px";
  banner.style.left = "50%";
  banner.style.transform = "translateX(-50%)";
  banner.style.background = "#111";
  banner.style.color = "#fff";
  banner.style.padding = "10px 14px";
  banner.style.borderRadius = "10px";
  banner.style.boxShadow = "0 4px 12px rgba(0,0,0,.3)";
  banner.style.display = "flex";
  banner.style.alignItems = "center";
  banner.style.gap = "12px";
  banner.style.zIndex = "9999";

  banner.innerHTML = `
    <span style="font-size:13px;">
      🔄 Nova versão disponível
    </span>
    <button style="
      background:#fff;
      color:#111;
      border:none;
      padding:6px 10px;
      border-radius:6px;
      cursor:pointer;
      font-size:12px;
    ">
      Atualizar
    </button>
  `;

  banner.querySelector("button").onclick = () => {
    worker.postMessage({ type: "SKIP_WAITING" });
  };

  document.body.appendChild(banner);
}

