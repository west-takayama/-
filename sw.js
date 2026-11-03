// Retire v1's permanent cache-first HTML. HTTP caching handles static files.
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil((async()=>{
  const keys=await caches.keys();
  await Promise.all(keys.filter(key=>key.startsWith('bridge-radio-')).map(key=>caches.delete(key)));
  await self.clients.claim();
})()));
// No fetch interception: failed audio requests must never return HTML.
