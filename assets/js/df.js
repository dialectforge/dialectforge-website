// DialectForge — minimal JS: nav toggle, copy buttons + demo dialect cycle meter. Site works without it.
(function(){
  var t=document.querySelector('.nav-toggle'),n=document.getElementById('nav');
  if(t&&n){t.addEventListener('click',function(){var o=n.classList.toggle('open');t.setAttribute('aria-expanded',o)})}
  document.querySelectorAll('[data-copy]').forEach(function(b){b.addEventListener('click',function(){
    var pre=b.parentNode.querySelector('pre');if(!pre)return;var txt=pre.textContent;
    function done(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1500)}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(done,function(){sel(pre)})}else{sel(pre)}
    function sel(el){var r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Press Ctrl+C'}
  })});
  var m=document.querySelector('[data-cycle]');if(!m)return;
  var bar=m.querySelector('i'),num=m.querySelector('b'),hex=document.querySelector('[data-hexline]');
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function rnd(){var s='';for(var i=0;i<13;i++){s+=("0"+Math.floor(Math.random()*256).toString(16)).slice(-2)+(i<12?' ':'')}return s}
  function tick(){var left=120-Math.floor(Date.now()/1000)%120;num.textContent=left;bar.style.width=((120-left)/120*100)+'%';
    if(hex&&!reduce&&(left===120||!hex.dataset.init)){hex.textContent=rnd();hex.dataset.init=1}}
  tick();setInterval(tick,1000);
})();
