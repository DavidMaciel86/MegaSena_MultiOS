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
