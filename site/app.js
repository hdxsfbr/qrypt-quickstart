// Tabs (arrow keys supported) and copy buttons. No analytics, no cookies, no network calls.
document.querySelectorAll('[role=tablist]').forEach(list=>{
  const tabs=[...list.querySelectorAll('[role=tab]')];
  const select=t=>{tabs.forEach(x=>{const on=x===t;x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;
    document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});t.focus();};
  tabs.forEach((t,i)=>{t.addEventListener('click',()=>select(t));
    t.addEventListener('keydown',e=>{const n={ArrowRight:1,ArrowLeft:-1}[e.key];
      if(n){e.preventDefault();select(tabs[(i+n+tabs.length)%tabs.length]);}});});
});
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{
  const txt=document.getElementById(b.dataset.target).innerText;
  try{await navigator.clipboard.writeText(txt);b.textContent='Copied';}catch{b.textContent='Select and copy';}
  setTimeout(()=>b.textContent='Copy',2000);
}));
