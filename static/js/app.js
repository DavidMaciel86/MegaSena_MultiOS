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
