// dishme service worker: the app and its recipe data work offline; the menu reader is cached after first use.
const SHELL = 'dishme-v3';
const FILES = ['./', './index.html', './data.js', './manifest.webmanifest', './icon-192.png', './icon-512.png'];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(SHELL).then((c) => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((k) => Promise.all(k.filter((x) => x !== SHELL).map((x) => caches.delete(x)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request).then((r) => { const cp = r.clone(); caches.open(SHELL).then((c) => c.put('./index.html', cp)); return r; }).catch(() => caches.match('./index.html')));
    return;
  }
  const cacheable = url.origin === location.origin || url.hostname === 'cdn.jsdelivr.net' || url.hostname === 'tessdata.projectnaptha.com' || url.hostname === 'fonts.gstatic.com' || url.hostname === 'fonts.googleapis.com';
  if (!cacheable) return;
  e.respondWith(caches.match(e.request).then((hit) => {
    const net = fetch(e.request).then((r) => { if (r.ok) { const cp = r.clone(); caches.open(SHELL).then((c) => c.put(e.request, cp)); } return r; });
    return url.origin === location.origin ? net.catch(() => hit) : (hit || net);
  }));
});
