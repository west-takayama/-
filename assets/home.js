'use strict';
window.requestTopic = function(topic) {
  switchFanTab('letter');
  const body = document.getElementById('letter-body');
  const line = 'テーマリクエスト：' + topic + '\n\n';
  if (!body.value.includes(line.trim())) body.value = (line + body.value).slice(0, 1500);
  body.dispatchEvent(new Event('input', {bubbles:true}));
  body.focus();
};
(() => {
  const allowed = new Set(['home', 'cast', 'blog', 'fan']);
  function applyHash() {
    const key = location.hash.replace('#', '');
    if (allowed.has(key)) switchPageById(key);
    if (key === 'fortune') {
      switchPageById('home');
      document.getElementById('horoscope-date').closest('section').scrollIntoView({block:'start'});
    }
  }
  const params = new URLSearchParams(location.search);
  if (params.get('to')) {
    const member = Object.values(profiles).find(p => p.letterTarget === params.get('to') || p.name === params.get('to'));
    if (member) { switchPageById('fan'); document.getElementById('letter-to').value = member.name; }
  }
  applyHash();
  window.addEventListener('hashchange', applyHash);
})();
