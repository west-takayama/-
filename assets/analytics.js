'use strict';
// Keep private previews out of the production property. No letter text or search input is sent.
(() => {
  if(location.hostname!=='spectacular-cuchufli-3e84ee.netlify.app')return;
  window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments);};
  const page=new URL(location.origin+location.pathname);
  for(const key of ['utm_source','utm_medium','utm_campaign']){const value=new URLSearchParams(location.search).get(key);if(value&&/^[a-zA-Z0-9_-]{1,100}$/.test(value))page.searchParams.set(key,value);}
  let referrer='';try{const r=new URL(document.referrer);referrer=r.origin+r.pathname;}catch{}
  gtag('js',new Date());gtag('config','G-E4REXF05WE',{page_location:page.href,page_referrer:referrer,allow_google_signals:false});
  const script=document.createElement('script');script.async=true;script.src='https://www.googletagmanager.com/gtag/js?id=G-E4REXF05WE';document.head.appendChild(script);
})();
