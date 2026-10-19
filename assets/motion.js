const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
if(!reducedMotion.matches&&'IntersectionObserver' in window){
 const revealObserver=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){entry.target.classList.add('is-visible');revealObserver.unobserve(entry.target)}}},{threshold:.06,rootMargin:'0px 0px -18px 0px'});
 document.querySelectorAll('.sectionhead,.productcard,.home-family-card,.catalog-card,.guidecard,.industry-card,.format,.step,.home-equipment-grid>article,.factory-gallery>figure,.tank-content>section,.guide-longform>section,.home-quality,.home-story-grid>article').forEach((element,index)=>{
  element.dataset.reveal='';element.style.setProperty('--reveal-delay',`${index%3*65}ms`);
  const bounds=element.getBoundingClientRect();if(bounds.top<innerHeight&&bounds.bottom>0)element.classList.add('is-visible');else revealObserver.observe(element);
 });
 document.documentElement.classList.add('motion-ready');
 reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches){document.documentElement.classList.remove('motion-ready');revealObserver.disconnect()}});
}

const productionRail=document.querySelector('#production-rail');
if(productionRail){
 let playing=!reducedMotion.matches;let hovered=false;let focused=false;let visible=false;let frame;let previousTime=0;let position=0;let direction=1;
 const stopFrame=()=>{cancelAnimationFrame(frame);frame=undefined;previousTime=0};
 const animate=time=>{
  if(previousTime){
   const limit=productionRail.scrollWidth-productionRail.clientWidth;
   position+=Math.min(time-previousTime,50)*.072*direction;
   if(position>=limit){position=limit;direction=-1}
   else if(position<=0){position=0;direction=1}
   productionRail.scrollLeft=position;
  }
  previousTime=time;frame=requestAnimationFrame(animate);
 };
 const sync=()=>{stopFrame();position=productionRail.scrollLeft;if(playing&&visible&&!hovered&&!focused&&!document.hidden)frame=requestAnimationFrame(animate)};
 const pause=()=>{playing=false;sync()};
 productionRail.addEventListener('pointerenter',()=>{hovered=true;sync()});
 productionRail.addEventListener('pointerleave',()=>{hovered=false;sync()});
 productionRail.addEventListener('pointerdown',pause,{passive:true});
 productionRail.addEventListener('wheel',pause,{passive:true});
 productionRail.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key))pause()});
 productionRail.addEventListener('focusin',()=>{focused=true;sync()});
 productionRail.addEventListener('focusout',event=>{focused=productionRail.contains(event.relatedTarget);sync()});
 document.addEventListener('visibilitychange',sync);
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()},{threshold:.05}).observe(productionRail);
 reducedMotion.addEventListener('change',()=>{playing=!reducedMotion.matches;sync()});
 sync();
}
