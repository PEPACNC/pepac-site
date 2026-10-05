(function(){
  // Mobile menu
  var t=document.querySelector('.menu-toggle'), n=document.getElementById('site-nav');
  if(t&&n){t.addEventListener('click',function(){var o=n.classList.toggle('open');t.setAttribute('aria-expanded',o);document.body.style.overflow=o?'hidden':'';});}

  // Donation widgets -> ActBlue link
  document.querySelectorAll('[data-donate]').forEach(function(w){
    var freq='once', amt='50', go=w.querySelector('[data-donate-go]'), other=w.querySelector('.other input');
    var base=go.getAttribute('href').split('?')[0], ref=(go.getAttribute('href').match(/refcode=([^&]+)/)||[])[1]||'website';
    function pick(group,btn){group.querySelectorAll('button').forEach(function(b){b.setAttribute('aria-checked',b===btn)});}
    function update(){
      var a=parseInt(amt,10)||0;
      go.href=base+'?refcode='+ref+(a?'&amount='+a:'')+(freq==='monthly'?'&recurring=1':'');
      go.textContent='Donate'+(a?' $'+a.toLocaleString():'')+(freq==='monthly'?' monthly':'');
    }
    w.querySelectorAll('[data-freq]').forEach(function(b){b.addEventListener('click',function(){freq=b.dataset.freq;pick(b.parentNode,b);update();});});
    w.querySelectorAll('[data-amt]').forEach(function(b){b.addEventListener('click',function(){amt=b.dataset.amt;if(other)other.value='';pick(b.parentNode,b);update();});});
    if(other)other.addEventListener('input',function(){amt=other.value;pick(other.closest('.amounts'),null);update();});
    update();
  });

  // Deadlines: mark past / next, add countdown
  var today=new Date();today.setHours(0,0,0,0);var nextSet=false;
  document.querySelectorAll('.deadlines li[data-date]').forEach(function(li){
    var d=new Date(li.dataset.date+'T00:00:00');
    if(d<today){li.classList.add('past');}
    else if(!nextSet){nextSet=true;li.classList.add('next');var days=Math.round((d-today)/864e5);
      var s=document.createElement('span');s.className='countdown';s.textContent=days===0?'Today':days===1?'Tomorrow':days+' days';li.querySelector('.label').appendChild(s);}
  });

  // Forms: send visitor back to this site's thank-you page
  document.querySelectorAll('form[data-form]').forEach(function(f){
    var nx=f.querySelector('input[name=_next]');
    if(nx){nx.value=location.origin+(document.documentElement.dataset.base||'')+'/thanks';}
  });
})();
