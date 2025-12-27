const CACHE_NAME = "megasurpresinhas-v6";

const ASSETS = [
  "/", // importante para fallback offline/navegação
  "/static/manifest.webmanifest",
  "/static/js/app.js",
  "/static/js/sw.js",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  if (req.method !== "GET") return;

  // 1) Navegação (HTML): network-first com fallback para cache da "/"
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put("/", copy));
          return resp;
        })
        .catch(() => caches.match("/"))
    );
    return;
  }

  // 2) Assets estáticos: stale-while-revalidate (cache rápido + atualiza em background)
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const fetchPromise = fetch(req).then((networkResp) => {
          caches.open(CACHE_NAME).then((cache) => cache.put(req, networkResp.clone()));
          return networkResp;
        }).catch(() => cached);

        return cached || fetchPromise;
      })
    );
    return;
  }

  // 3) Demais requests: network com fallback no cache
  event.respondWith(
    fetch(req).catch(() => caches.match(req))
  );
});
