"use strict";
/* App logic — data lives in data.js */
"use strict";

const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
$("#capabilityGrid").innerHTML = CAPABILITIES.map(c => `<article class="card"><div class="num">${esc(c.n)}</div><h3>${esc(c.t)}</h3><p>${esc(c.d)}</p><div class="tags">${c.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</div></article>`).join("");
const LEVEL_LABEL = {"hands-on":"Hands-on","working":"Working knowledge","learning":"Currently learning"};
$("#skillGrid").innerHTML = SKILLS.map(s => `<div class="skill"><strong><i class="dot ${esc(s.level)}" aria-hidden="true"></i>${esc(s.t)}</strong><span>${esc(s.d)}</span></div>`).join("");
$("#projectGrid").innerHTML = PROJECTS.map((p,i) => `<article class="card project" data-category="${esc(p.cat)}"><div class="status">${esc(p.status)}</div><h3>${esc(p.t)}</h3><p>${esc(p.d)}</p><div class="tags">${p.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</div><div class="details"><button class="textlink" type="button" data-project="${i}" aria-haspopup="dialog">View project brief ↗</button></div></article>`).join("");
(function(){ const links=[]; if(CONFIG.linkedin)links.push(`<a href="${esc(CONFIG.linkedin)}" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a>`); if(CONFIG.github)links.push(`<a href="${esc(CONFIG.github)}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>`); if(CONFIG.resumeUrl)links.push(`<a href="${esc(CONFIG.resumeUrl)}" download>Download résumé ↓</a>`); $("#socialRow").innerHTML=links.join(""); })();
const themeBtn = $("#themeBtn");
function syncThemeBtn(){ const light=document.documentElement.dataset.theme==="light"; themeBtn.textContent=light?"☾":"☼"; themeBtn.setAttribute("aria-label",light?"Switch to dark theme":"Switch to light theme"); themeBtn.setAttribute("aria-pressed",String(light)); }
themeBtn.addEventListener("click",()=>{ const next=document.documentElement.dataset.theme==="light"?"dark":"light"; document.documentElement.dataset.theme=next; try{localStorage.setItem("portfolio-theme",next);}catch(e){} syncThemeBtn(); });
syncThemeBtn();
const menuBtn=$("#menuBtn"),navlinks=$("#navlinks");
menuBtn.addEventListener("click",()=>{ const open=navlinks.classList.toggle("open"); menuBtn.setAttribute("aria-expanded",String(open)); menuBtn.setAttribute("aria-label",open?"Close menu":"Open menu"); });
$$("#navlinks a").forEach(a=>a.addEventListener("click",()=>{ navlinks.classList.remove("open"); menuBtn.setAttribute("aria-expanded","false"); }));
const resultCount=$("#resultCount");
function applyFilter(f){ let shown=0; $$(".project").forEach(p=>{ const show=f==="all"||p.dataset.category===f; p.hidden=!show; if(show)shown++; }); resultCount.textContent=`Showing ${shown} of ${PROJECTS.length} projects`; }
$$(".filter").forEach(btn=>btn.addEventListener("click",()=>{ $$(".filter").forEach(b=>b.setAttribute("aria-pressed","false")); btn.setAttribute("aria-pressed","true"); applyFilter(btn.dataset.filter); }));
applyFilter("all");
const modal=$("#modal"),closeBtn=$("#closeModal"); let lastFocus=null;
function openModal(i){ const p=PROJECTS[i]; $("#modalTitle").textContent=p.t; $("#modalDesc").textContent=p.brief; lastFocus=document.activeElement; modal.hidden=false; modal.classList.add("show"); document.body.style.overflow="hidden"; closeBtn.focus(); }
function closeModal(){ modal.classList.remove("show"); modal.hidden=true; document.body.style.overflow=""; if(lastFocus)lastFocus.focus(); }
$("#projectGrid").addEventListener("click",e=>{ const btn=e.target.closest("[data-project]"); if(btn)openModal(Number(btn.dataset.project)); });
closeBtn.addEventListener("click",closeModal);
modal.addEventListener("click",e=>{ if(e.target===modal)closeModal(); });
document.addEventListener("keydown",e=>{ if(modal.hidden)return; if(e.key==="Escape")closeModal(); if(e.key==="Tab"){ const f=$$("button,a[href],input,textarea",modal).filter(el=>!el.disabled); if(!f.length)return; const first=f[0],last=f[f.length-1]; if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();} else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();} } });
const formMsg=$("#formMsg");
function showMsg(t,k){ formMsg.textContent=t; formMsg.className="form-msg "+(k||""); }
$("#contactForm").addEventListener("submit",e=>{ e.preventDefault(); const name=$("#visitor").value.trim(),email=$("#email").value.trim(),msg=$("#message").value.trim(); if(!name||!email||!msg){showMsg("Please fill in your name, email and a message.","error");return;} if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){showMsg("That email address doesn't look valid — please check it.","error");$("#email").focus();return;} if(!CONFIG.email){showMsg("Contact email isn't configured yet. Please add CONFIG.email in the code (see docs/CONTENT-CHECKLIST.md).","error");return;} const subject=encodeURIComponent("Portfolio enquiry from "+name); const body=encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\n${msg}`); showMsg("Opening your email app…","ok"); location.href=`mailto:${CONFIG.email}?subject=${subject}&body=${body}`; });
$("#copyEmailBtn").addEventListener("click",async()=>{ if(!CONFIG.email){showMsg("Contact email isn't configured yet. Please add CONFIG.email in the code.","error");return;} try{await navigator.clipboard.writeText(CONFIG.email);showMsg("Email copied: "+CONFIG.email,"ok");}catch(e){showMsg("Couldn't copy automatically — my email is "+CONFIG.email,"error");} });
const navMap=new Map($$(".links a").map(a=>[a.getAttribute("href").slice(1),a]));
const spy=new IntersectionObserver(entries=>{ entries.forEach(en=>{ if(en.isIntersecting){ navMap.forEach(a=>a.classList.remove("active")); const link=navMap.get(en.target.id); if(link)link.classList.add("active"); } }); },{rootMargin:"-40% 0px -55% 0px"});
$$("main section[id]").forEach(s=>spy.observe(s));
$("#year").textContent=new Date().getFullYear();
