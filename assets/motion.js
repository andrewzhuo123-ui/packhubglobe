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
 const section=productionRail.closest('section');const track=productionRail.querySelector('.process-track');const stages=[...track.children];
 const toggle=section.querySelector('[data-process-toggle]');
 let playing=!reducedMotion.matches;let hovered=false;let focused=false;let visible=false;let frame;let previousTime=0;let position=0;
 for(const stage of stages){const clone=stage.cloneNode(true);clone.setAttribute('aria-hidden','true');clone.inert=true;track.append(clone)}
 const cycleWidth=()=>track.children[stages.length].offsetLeft-track.children[0].offsetLeft;
 const stopFrame=()=>{cancelAnimationFrame(frame);frame=undefined;previousTime=0};
 const animate=time=>{
  if(previousTime){position+=Math.min(time-previousTime,50)*.024;const width=cycleWidth();if(position>=width)position-=width;productionRail.scrollLeft=position}
  previousTime=time;frame=requestAnimationFrame(animate);
 };
 const sync=()=>{stopFrame();position=productionRail.scrollLeft;if(playing&&visible&&!hovered&&!focused&&!document.hidden)frame=requestAnimationFrame(animate)};
 const setPlaying=value=>{playing=value;toggle.textContent=playing?'Pause motion':'Play motion';toggle.setAttribute('aria-pressed',String(!playing));sync()};
 toggle.addEventListener('click',()=>setPlaying(!playing));
 section.querySelector('[data-process-prev]').addEventListener('click',()=>{setPlaying(false);if(productionRail.scrollLeft<10)productionRail.scrollLeft=cycleWidth();productionRail.scrollBy({left:-(stages[0].offsetWidth+24),behavior:reducedMotion.matches?'auto':'smooth'})});
 section.querySelector('[data-process-next]').addEventListener('click',()=>{setPlaying(false);productionRail.scrollBy({left:stages[0].offsetWidth+24,behavior:reducedMotion.matches?'auto':'smooth'})});
 productionRail.addEventListener('pointerenter',()=>{hovered=true;sync()});
 productionRail.addEventListener('pointerleave',()=>{hovered=false;sync()});
 productionRail.addEventListener('pointerdown',()=>setPlaying(false),{passive:true});
 productionRail.addEventListener('wheel',()=>setPlaying(false),{passive:true});
 productionRail.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key))setPlaying(false)});
 section.addEventListener('focusin',()=>{focused=true;sync()});
 section.addEventListener('focusout',event=>{focused=section.contains(event.relatedTarget);sync()});
 document.addEventListener('visibilitychange',sync);
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()},{threshold:.05}).observe(productionRail);
 reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches)setPlaying(false)});
 setPlaying(playing);
}
