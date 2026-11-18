# clock.py – die Live-Uhr fuer das HMFS-Dashboard.
#
# Enthaelt CSS, Markup und JavaScript als reine Strings und klebt sie in die
# Seite, die build.py erzeugt. Laeuft vollstaendig im Browser des Betrachters:
# keine API, kein Key, kein Netzwerk. Deshalb tickt sie weiter, auch wenn die
# Kursdaten darunter von heute morgen sind.

CSS = """
:root{
  --k-card:#141822; --k-card2:#1a1f2b; --k-bd:#242b3a;
  --k-ink:#e6e9ef; --k-ink2:#99a3b8; --k-ink3:#5d6779;
  --k-open:#3fb950; --k-edge:#d29922; --k-shut:#49536a; --k-now:#58a6ff;
  --k-mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}
.kb{position:sticky;top:0;z-index:30;background:rgba(11,14,20,.93);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--k-bd)}
.kb-in{max-width:880px;margin:0 auto;display:flex;align-items:center;gap:14px;
  padding:11px 16px;cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent}
.kb-mk{min-width:0;flex:1}
.kb-nm{font-size:14px;font-weight:600;display:flex;align-items:center;gap:8px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--k-ink)}
.kb-sub{font-size:11.5px;color:var(--k-ink3);margin-top:3px;font-variant-numeric:tabular-nums}
.kb-cl{font-family:var(--k-mono);font-size:26px;font-weight:700;line-height:1;
  letter-spacing:-.02em;font-variant-numeric:tabular-nums;text-align:right;color:var(--k-ink)}
.kb-cl .sec{color:var(--k-ink3);font-size:.55em;font-weight:500}
.kb-cl small{display:block;font-family:inherit;font-size:10px;font-weight:500;
  color:var(--k-ink3);letter-spacing:.05em;margin-top:4px;font-family:-apple-system,sans-serif}
.kb-chev{flex:none;color:var(--k-ink3);transition:transform .22s ease;font-size:13px}
.kb.open .kb-chev{transform:rotate(180deg)}
.kb-chip{font-family:var(--k-mono);font-size:11px;font-weight:700;
  background:rgba(63,185,80,.14);color:#82e08f;padding:2px 7px;border-radius:5px}

.kp{max-height:0;overflow:hidden;transition:max-height .3s ease;
  border-bottom:1px solid var(--k-bd)}
.kb.open + .kp{max-height:2400px;overflow:auto}
.kp-in{max-width:880px;margin:0 auto;padding:2px 16px 20px}
.kp h3{font-size:11px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;
  color:var(--k-ink3);margin:20px 0 9px}

.kg{display:grid;gap:9px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.kx{background:var(--k-card);border:1px solid var(--k-bd);border-radius:11px;
  padding:13px 14px;display:flex;flex-direction:column;gap:10px;cursor:pointer;
  transition:border-color .15s}
.kx.live{background:var(--k-card2);border-color:#2e4a35}
.kx.sel{box-shadow:0 0 0 1.5px var(--k-now)}
.kx-r1{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.kx-nm{font-size:14px;font-weight:600;line-height:1.25;color:var(--k-ink)}
.kx-cy{font-size:11.5px;color:var(--k-ink3);margin-top:2px}
.kx-lt{font-family:var(--k-mono);font-size:18px;font-weight:500;text-align:right;
  font-variant-numeric:tabular-nums;line-height:1.1;color:var(--k-ink)}
.kx-lt small{display:block;font-family:-apple-system,sans-serif;font-size:10px;
  font-weight:500;color:var(--k-ink3);letter-spacing:.04em;margin-top:3px}
.kpill{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;font-weight:600;
  padding:3px 9px 3px 7px;border-radius:999px;white-space:nowrap}
.kdot{width:7px;height:7px;border-radius:50%;flex:none}
.s-open{color:#82e08f;background:rgba(63,185,80,.13)} .s-open .kdot{background:var(--k-open)}
.s-edge{color:#e8c26a;background:rgba(210,153,34,.13)} .s-edge .kdot{background:var(--k-edge)}
.s-shut{color:#8a94a8;background:rgba(73,83,106,.16)} .s-shut .kdot{background:var(--k-shut)}
.kbar{height:5px;background:#1f2533;border-radius:3px;overflow:hidden}
.kbar i{display:block;height:100%;border-radius:3px;background:var(--k-open);
  transition:width .9s linear}
.kx:not(.live) .kbar i{background:var(--k-shut)}
.kcd{display:flex;justify-content:space-between;gap:10px;font-size:12px;color:var(--k-ink2)}
.kcd span:last-child{font-family:var(--k-mono);color:var(--k-ink);font-weight:500;
  font-variant-numeric:tabular-nums}
.ksess{font-size:10.5px;color:var(--k-ink3);font-family:var(--k-mono);
  display:flex;gap:9px;flex-wrap:wrap}

.ktl{background:var(--k-card);border:1px solid var(--k-bd);border-radius:11px;
  padding:15px 14px 9px}
.ktl-row{display:grid;grid-template-columns:118px 1fr;align-items:center;gap:11px;height:25px}
.ktl-lbl{font-size:11.5px;color:var(--k-ink2);text-align:right;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.ktrack{position:relative;height:9px;background:#1b2130;border-radius:4px}
.kseg{position:absolute;top:0;height:9px;border-radius:4px;background:#2f6b3a}
.kseg.ext{background:#3a3520;height:5px;top:2px;border-radius:3px}
.ktl-row.live .kseg:not(.ext){background:var(--k-open)}
.kaxis{display:grid;grid-template-columns:118px 1fr;gap:11px;margin-top:3px}
.kticks{position:relative;height:17px;font-family:var(--k-mono);font-size:10px;color:var(--k-ink3)}
.ktick{position:absolute;transform:translateX(-50%);top:3px}
.know{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--k-now);
  border-radius:1px;z-index:3}
.kleg{display:flex;gap:15px;flex-wrap:wrap;margin-top:13px;font-size:11.5px;
  color:var(--k-ink3);align-items:center}
.kleg i{display:inline-block;width:10px;height:10px;border-radius:3px;
  margin-right:6px;vertical-align:-1px}
.khint{font-size:11.5px;color:var(--k-ink3);margin:10px 0 0;line-height:1.6}
@media(max-width:540px){
  .ktl-row,.kaxis{grid-template-columns:76px 1fr;gap:8px}
  .ktl-lbl{font-size:10.5px}
  .kb-cl{font-size:22px}
}
"""

HTML = """
<div class="kb" id="kb">
  <div class="kb-in" id="kbIn">
    <div class="kb-mk">
      <div class="kb-nm"><span id="kbNm">-</span><span id="kbPill"></span></div>
      <div class="kb-sub"><span id="kbSub">-</span> <span class="kb-chip" id="kbTally"></span></div>
    </div>
    <div class="kb-cl" id="kbCl">--:--<span class="sec">:--</span><small id="kbCy"></small></div>
    <div class="kb-chev">&#9660;</div>
  </div>
</div>
<div class="kp">
  <div class="kp-in">
    <div id="kRegions"></div>
    <h3>Tagesverlauf (deine Zeit)</h3>
    <div class="ktl" id="kTl"></div>
    <div class="kleg">
      <span><i style="background:#3fb950"></i>Haupthandel offen</span>
      <span><i style="background:#2f6b3a"></i>Haupthandel zu</span>
      <span><i style="background:#3a3520;height:6px"></i>Vor-/Nachboerse</span>
      <span><i style="background:#58a6ff;width:3px;border-radius:1px"></i>jetzt</span>
    </div>
    <p class="khint">Tippe eine Boerse an, um sie ins Banner zu setzen. Feiertage sind
    noch nicht beruecksichtigt - nur Wochenenden.</p>
  </div>
</div>
"""

JS = """
(function(){
const EX = [
  {id:'xetra', nm:'Xetra', cy:'Frankfurt', sub:'DAX-Referenz', tz:'Europe/Berlin', rg:'Europa',
   ss:[{k:'open',l:'Haupthandel',a:540,b:1050}]},
  {id:'tradegate', nm:'Tradegate', cy:'Berlin', sub:'Vor-/Nachboerse DE', tz:'Europe/Berlin', rg:'Europa',
   ss:[{k:'pre',l:'Vorboerse',a:480,b:540},
       {k:'open',l:'Haupthandel',a:540,b:1050},
       {k:'post',l:'Nachboerse',a:1050,b:1320}]},
  {id:'lse', nm:'London Stock Exchange', cy:'London', sub:'', tz:'Europe/London', rg:'Europa',
   ss:[{k:'pre',l:'Pre-Auction',a:305,b:480},
       {k:'open',l:'Haupthandel',a:480,b:990},
       {k:'post',l:'Post-Close',a:990,b:1035}]},
  {id:'euronext', nm:'Euronext', cy:'Paris', sub:'Amsterdam', tz:'Europe/Paris', rg:'Europa',
   ss:[{k:'open',l:'Haupthandel',a:540,b:1050},
       {k:'post',l:'Nachboerse',a:1060,b:1080}]},
  {id:'six', nm:'SIX Swiss Exchange', cy:'Zuerich', sub:'', tz:'Europe/Zurich', rg:'Europa',
   ss:[{k:'open',l:'Haupthandel',a:540,b:1040}]},
  {id:'us', nm:'NYSE / Nasdaq', cy:'New York', sub:'', tz:'America/New_York', rg:'Nordamerika',
   ss:[{k:'pre',l:'Pre-Market',a:240,b:570},
       {k:'open',l:'Haupthandel',a:570,b:960},
       {k:'post',l:'After-Hours',a:960,b:1200}]},
  {id:'tsx', nm:'Toronto Stock Exchange', cy:'Toronto', sub:'', tz:'America/Toronto', rg:'Nordamerika',
   ss:[{k:'pre',l:'Pre-Market',a:420,b:570},
       {k:'open',l:'Haupthandel',a:570,b:960}]},
  {id:'tse', nm:'Tokyo Stock Exchange', cy:'Tokio', sub:'', tz:'Asia/Tokyo', rg:'Asien',
   ss:[{k:'open',l:'Vormittag',a:540,b:690},
       {k:'open',l:'Nachmittag',a:750,b:930}]},
  {id:'hkex', nm:'Hong Kong Exchange', cy:'Hongkong', sub:'', tz:'Asia/Hong_Kong', rg:'Asien',
   ss:[{k:'open',l:'Vormittag',a:570,b:720},
       {k:'open',l:'Nachmittag',a:780,b:960}]}
];
const ORDER = ['Europa','Nordamerika','Asien'];
const WORK = {Mon:1,Tue:1,Wed:1,Thu:1,Fri:1};
const WD = {Mon:'Mo',Tue:'Di',Wed:'Mi',Thu:'Do',Fri:'Fr',Sat:'Sa',Sun:'So'};
const SHIFT = {Mon:0,Tue:1,Wed:2,Thu:3,Fri:4,Sat:5,Sun:6};
const NAME_OF = {}; for(const k in SHIFT) NAME_OF[SHIFT[k]] = k;

const p2 = n => String(n).padStart(2,'0');
const hm = m => p2(Math.floor(m/60))+':'+p2(Math.round(m%60));

function parts(d, tz){
  const f = new Intl.DateTimeFormat('en-GB',{timeZone:tz,weekday:'short',
    year:'numeric',month:'2-digit',day:'2-digit',
    hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
  const o = {}; for(const x of f.formatToParts(d)) o[x.type] = x.value;
  return {wd:o.weekday,h:+o.hour%24,m:+o.minute,s:+o.second,
          y:+o.year,mo:+o.month,dy:+o.day};
}
function zoneOffset(d, tz){
  const p = parts(d, tz);
  return Math.round((Date.UTC(p.y,p.mo-1,p.dy,p.h,p.m,p.s)
    - Math.floor(d.getTime()/1000)*1000)/60000);
}
const reg = e => { const o = e.ss.filter(s=>s.k==='open');
  return {a:o[0].a, b:o[o.length-1].b}; };

function untilNextOpen(e, wd, nowMin){
  const r = reg(e), start = SHIFT[wd];
  for(let d=0; d<9; d++){
    if(!WORK[NAME_OF[(start+d)%7]]) continue;
    const t = d*1440 + r.a;
    if(t > nowMin) return t - nowMin;
  }
  return null;
}
function state(e, now){
  const p = parts(now, e.tz);
  const nowMin = p.h*60 + p.m + p.s/60;
  const r = reg(e);
  const weekend = !WORK[p.wd];
  const cur = weekend ? null : (e.ss.find(s => nowMin >= s.a && nowMin < s.b) || null);
  const opens = e.ss.filter(s=>s.k==='open');
  const inBreak = !weekend && !cur && nowMin > opens[0].a && nowMin < r.b;
  let kind,label,cdL,cdM;
  if(cur && cur.k==='open'){ kind='open'; label='Geoeffnet'; cdL='Schluss in'; cdM=cur.b-nowMin; }
  else if(cur && cur.k==='pre'){ kind='edge'; label=cur.l; cdL='Eroeffnung in'; cdM=r.a-nowMin; }
  else if(cur && cur.k==='post'){ kind='edge'; label=cur.l; cdL='Ende in'; cdM=cur.b-nowMin; }
  else if(inBreak){ kind='edge'; label='Mittagspause'; cdL='Fortsetzung in';
    cdM = opens.find(s=>s.a > nowMin).a - nowMin; }
  else { kind='shut'; label = weekend ? 'Wochenende' : 'Geschlossen';
    cdL='Eroeffnung in'; cdM = untilNextOpen(e, p.wd, nowMin); }
  const prog = kind==='shut' ? 0 : Math.max(0, Math.min(1, (nowMin-r.a)/(r.b-r.a)));
  return {kind,label,cdL,cdM,prog,reg:r,wd:WD[p.wd],
          time:p2(p.h)+':'+p2(p.m), sec:p2(p.s), isOpen:kind==='open'};
}
function dur(m){
  if(m==null) return '-';
  const t = Math.max(0, Math.round(m));
  const d = Math.floor(t/1440), h = Math.floor(t%1440/60), mm = t%60;
  if(d) return d+' T '+h+' h';
  if(h) return h+' h '+p2(mm)+' min';
  return mm+' min';
}

let sel = 'xetra';
try{ const s = localStorage.getItem('hmfs.market');
     if(s && EX.some(e=>e.id===s)) sel = s; }catch(_){}

const wrapR = document.getElementById('kRegions'), N = {};
for(const rg of ORDER){
  const h = document.createElement('h3'); h.textContent = rg; wrapR.appendChild(h);
  const g = document.createElement('div'); g.className = 'kg';
  for(const e of EX.filter(x=>x.rg===rg)){
    const c = document.createElement('div'); c.className = 'kx';
    c.innerHTML = '<div class="kx-r1"><div><div class="kx-nm">'+e.nm+'</div>'
      + '<div class="kx-cy">'+e.cy+(e.sub?' &middot; '+e.sub:'')+'</div></div>'
      + '<div class="kx-lt"><span data-t></span><small data-wd></small></div></div>'
      + '<div data-pill></div><div class="kbar"><i data-bar></i></div>'
      + '<div class="kcd"><span data-cl></span><span data-cv></span></div>'
      + '<div class="ksess">'
      + e.ss.map(s=>'<span>'+s.l+' '+hm(s.a)+'-'+hm(s.b)+'</span>').join('')
      + '</div>';
    c.addEventListener('click', ev => { ev.stopPropagation(); pick(e.id); });
    g.appendChild(c);
    N[e.id] = {card:c, t:c.querySelector('[data-t]'), wd:c.querySelector('[data-wd]'),
      pill:c.querySelector('[data-pill]'), bar:c.querySelector('[data-bar]'),
      cl:c.querySelector('[data-cl]'), cv:c.querySelector('[data-cv]')};
  }
  wrapR.appendChild(g);
}

const tl = document.getElementById('kTl'), T = {};
for(const e of EX){
  const r = document.createElement('div'); r.className = 'ktl-row';
  r.innerHTML = '<div class="ktl-lbl">'+e.nm+'</div><div class="ktrack"></div>';
  tl.appendChild(r);
  T[e.id] = {row:r, track:r.querySelector('.ktrack')};
}
const ax = document.createElement('div'); ax.className = 'kaxis';
ax.innerHTML = '<div></div><div class="kticks"></div>';
tl.appendChild(ax);
for(let h=0; h<=24; h+=3){
  const s = document.createElement('span'); s.className = 'ktick';
  s.style.left = (h/24*100)+'%'; s.textContent = p2(h%24);
  ax.querySelector('.kticks').appendChild(s);
}

function pick(id){
  sel = id;
  try{ localStorage.setItem('hmfs.market', id); }catch(_){}
  tick();
}
const kb = document.getElementById('kb');
document.getElementById('kbIn').addEventListener('click', ()=>kb.classList.toggle('open'));

let built = false;
function tick(){
  const now = new Date();
  const localOff = -now.getTimezoneOffset();
  const nowLocal = now.getHours()*60 + now.getMinutes() + now.getSeconds()/60;
  let open = 0;
  for(const e of EX){
    const st = state(e, now), n = N[e.id];
    if(st.isOpen) open++;
    n.t.textContent = st.time;
    n.wd.textContent = st.wd;
    n.pill.innerHTML = '<span class="kpill s-'+st.kind+'"><span class="kdot"></span>'
      + st.label+'</span>';
    n.bar.style.width = (st.prog*100).toFixed(2)+'%';
    n.cl.textContent = st.cdL;
    n.cv.textContent = dur(st.cdM);
    n.card.classList.toggle('live', st.isOpen);
    n.card.classList.toggle('sel', e.id===sel);

    const tn = T[e.id];
    tn.row.classList.toggle('live', st.isOpen);
    if(!built){
      const delta = zoneOffset(now, e.tz) - localOff;
      const map = m => (((m - delta)%1440)+1440)%1440;
      const segs = [];
      const push = (a,b,cls) => {
        const x = map(a), y = map(b);
        if(y > x) segs.push([x,y,cls]);
        else { segs.push([x,1440,cls]); segs.push([0,y,cls]); }
      };
      for(const s of e.ss) if(s.k !== 'open') push(s.a, s.b, 'ext');
      const r = reg(e); push(r.a, r.b, '');
      tn.track.innerHTML = segs.map(function(sg){
        return '<div class="kseg '+sg[2]+'" style="left:'+(sg[0]/1440*100).toFixed(3)
          + '%;width:'+((sg[1]-sg[0])/1440*100).toFixed(3)+'%"></div>';
      }).join('') + '<div class="know" data-now></div>';
    }
    const nl = tn.track.querySelector('[data-now]');
    if(nl) nl.style.left = (nowLocal/1440*100).toFixed(3)+'%';
  }
  built = true;

  const e = EX.find(x=>x.id===sel) || EX[0];
  const st = state(e, now);
  document.getElementById('kbNm').textContent = e.nm;
  document.getElementById('kbPill').innerHTML =
    '<span class="kpill s-'+st.kind+'"><span class="kdot"></span>'+st.label+'</span>';
  document.getElementById('kbSub').textContent = st.cdL+' '+dur(st.cdM)+' \\u00b7';
  document.getElementById('kbCl').innerHTML = st.time
    + '<span class="sec">:'+st.sec+'</span><small>'+e.cy+'</small>';
  document.getElementById('kbTally').textContent = open+'/'+EX.length+' offen';
}
tick();
setInterval(tick, 1000);
})();
"""


def inject(page):
    """Haengt das Uhr-CSS in den <head>, das Banner direkt hinter <body>
    und das Skript vor </body>. Gibt die fertige Seite zurueck."""
    page = page.replace("</head>", "<style>" + CSS + "</style></head>", 1)
    page = page.replace("<body>", "<body>" + HTML, 1)
    page = page.replace("</body>", "<script>" + JS + "</script></body>", 1)
    return page
