const CACHE_NAME = "megasurpresinhas-v5";

const ASSETS = [
  "/static/manifest.webmanifest",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png"
];

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Só intercepta GET
  if (req.method !== "GET") return;

  // 1) Para navegação (HTML), use network-first
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          // Atualiza o cache da página inicial
          const copy = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put("/", copy));
          return resp;
        })
        .catch(() => caches.match("/") )
    );
    return;
  }

  // 2) Para assets estáticos (/static), use cache-first
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(req).then((cached) => cached || fetch(req))
    );
    return;
  }

  // 3) Para o resto, padrão: network com fallback cache
  event.respondWith(
    fetch(req).catch(() => caches.match(req))
  );
});
