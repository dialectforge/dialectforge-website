// DialectForge — minimal JS: nav toggle + demo dialect cycle meter. Site works without it.
(function(){
  var t=document.querySelector('.nav-toggle'),n=document.getElementById('nav');
  if(t&&n){t.addEventListener('click',function(){var o=n.classList.toggle('open');t.setAttribute('aria-expanded',o)})}
  var m=document.querySelector('[data-cycle]');if(!m)return;
  var bar=m.querySelector('i'),num=m.querySelector('b'),hex=document.querySelector('[data-hexline]');
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function rnd(){var s='';for(var i=0;i<13;i++){s+=("0"+Math.floor(Math.random()*256).toString(16)).slice(-2)+(i<12?' ':'')}return s}
  function tick(){var left=120-Math.floor(Date.now()/1000)%120;num.textContent=left;bar.style.width=((120-left)/120*100)+'%';
    if(hex&&!reduce&&(left===120||!hex.dataset.init)){hex.textContent=rnd();hex.dataset.init=1}}
  tick();setInterval(tick,1000);
})();
