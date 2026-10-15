// Tabs (arrow keys supported) and copy buttons. No analytics, no cookies, no network calls.
document.querySelectorAll('[role=tablist]').forEach(list=>{
  const tabs=[...list.querySelectorAll('[role=tab]')];
  const select=t=>{tabs.forEach(x=>{const on=x===t;x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;
    document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});t.focus();};
  tabs.forEach((t,i)=>{t.addEventListener('click',()=>select(t));
    t.addEventListener('keydown',e=>{const n={ArrowRight:1,ArrowLeft:-1}[e.key];
      if(n){e.preventDefault();select(tabs[(i+n+tabs.length)%tabs.length]);}
      if(e.key==='Home'){e.preventDefault();select(tabs[0]);}if(e.key==='End'){e.preventDefault();select(tabs[tabs.length-1]);}});});
});
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{
  const txt=document.getElementById(b.dataset.target).textContent; // exact code; CSS line numbers are not text
  const live=document.getElementById('copy-status');
  try{await navigator.clipboard.writeText(txt);b.textContent='Copied';if(live)live.textContent=b.getAttribute('aria-label').replace('Copy','Copied');}
  catch{b.textContent='Select and copy';if(live)live.textContent='Copy failed: select the code and copy it manually';}
  setTimeout(()=>b.textContent='Copy',2000);
}));
// Mobile docs menu: collapsible sidebar, Escape closes and returns focus.
(()=>{const b=document.querySelector('.menu'),w=document.querySelector('.wrap');if(!b)return;
const set=o=>{w.classList.toggle('open',o);b.setAttribute('aria-expanded',o);};
b.addEventListener('click',()=>{const o=b.getAttribute('aria-expanded')!=='true';set(o);if(o)document.querySelector('#sidebar a').focus();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&w.classList.contains('open')){set(false);b.focus();}});
document.querySelectorAll('#sidebar a').forEach(a=>a.addEventListener('click',()=>set(false)));})();

// Open a <details> when the URL hash points at it (sidebar "AI coding agents").
(()=>{const open=()=>{const id=location.hash.slice(1);if(!id)return;
  const el=document.getElementById(id);if(el&&el.tagName==="DETAILS"){el.open=true;el.scrollIntoView({block:"start"});}};
open();addEventListener("hashchange",open);})();
