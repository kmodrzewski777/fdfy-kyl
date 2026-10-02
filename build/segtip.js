(()=>{const tt=document.createElement('div');tt.className='seg-tt';tt.hidden=true;document.body.appendChild(tt);
 const hide=()=>{tt.hidden=true;};
 document.addEventListener('click',e=>{if(e.target.closest('.seg-tt'))return;const cr=e.target.closest('[data-camp]');if(!cr){hide();return;}const cid=cr.dataset.camp;
  tt.innerHTML=`<div class="tt-col"><button type="button" class="tt-del">Ukryj w raporcie</button></div>`;
  tt.querySelector('.tt-del').onclick=ev=>{ev.stopPropagation();tt.innerHTML=`<div class="tt-col"><span class="tt-q">Ukryć „${esc(FLOWS.c[cid].n)}” w raporcie?</span><div class="tt-row"><button type="button" class="tt-yes">Tak, ukryj</button><button type="button" class="tt-no">Anuluj</button></div></div>`;
   tt.querySelector('.tt-no').onclick=ev2=>{ev2.stopPropagation();hide();};tt.querySelector('.tt-yes').onclick=ev2=>{ev2.stopPropagation();hide();flHide(cid,true);};};
  tt.hidden=false;const x=Math.min(e.clientX+12,innerWidth-tt.offsetWidth-10),y=Math.min(e.clientY+12,innerHeight-tt.offsetHeight-10);tt.style.left=x+'px';tt.style.top=y+'px';});
 addEventListener('scroll',hide,{passive:true});document.addEventListener('keydown',e=>{if(e.key==='Escape')hide();});})();
