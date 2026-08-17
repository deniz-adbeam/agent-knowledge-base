#!/usr/bin/env python3
"""Build a knowledge graph from the Markdown notes in knowledge/.

Source of truth: OKF-style Markdown (YAML frontmatter + standard markdown links).
Outputs (both DERIVED, regenerable at any time):
  - graph.json : nodes + edges, for the agent to traverse relationships fast.
  - graph.html : self-contained, interactive graph view for humans (open in a browser).

No external dependencies; standard library only.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(ROOT, "knowledge")
MEMORY_DIR = os.path.join(ROOT, "memory")
OUT_JSON = os.path.join(ROOT, "graph.json")
OUT_HTML = os.path.join(ROOT, "graph.html")
TYPES_CONFIG = os.path.join(ROOT, "okf-types.json")

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
MD_LINK = re.compile(r"\]\((/[^)]+?\.md)\)")  # OKF bundle-relative markdown link
RESERVED = {"index.md", "log.md"}             # OKF reserved filenames (not concepts)
DIR_DESC = {
    "knowledge": "Durable facts, systems, and process know-how.",
    "memory": "Dated design-session and clarification episodes.",
}


def parse_frontmatter(text):
  """Parse a small, constrained subset of YAML frontmatter. Returns (meta, body)."""
  if not text.startswith("---"):
    return {}, text
  lines = text.split("\n")
  end = None
  for i in range(1, len(lines)):
    if lines[i].strip() == "---":
      end = i
      break
  if end is None:
    return {}, text
  fm = lines[1:end]
  body = "\n".join(lines[end + 1:])
  meta = {}
  i = 0
  while i < len(fm):
    line = fm[i]
    if not line.strip() or line.lstrip().startswith("#"):
      i += 1
      continue
    m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
    if not m:
      i += 1
      continue
    key, val = m.group(1), m.group(2).strip()
    if val == "":
      items = []
      j = i + 1
      while j < len(fm) and re.match(r"^\s*-\s+", fm[j]):
        items.append(re.sub(r"^\s*-\s+", "", fm[j]).strip())
        j += 1
      meta[key] = items
      i = j
    elif val.startswith("[") and val.endswith("]"):
      inner = val[1:-1].strip()
      meta[key] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
      i += 1
    else:
      meta[key] = val
      i += 1
  return meta, body


def first_sentence(body):
  for ln in body.split("\n"):
    s = ln.strip()
    if s and not s.startswith("#") and not s[0].isdigit():
      return re.sub(r"\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]", r"\1", s)[:220]
  return ""


def concept_id(path):
  rel = os.path.relpath(path, ROOT)
  return rel[:-3] if rel.endswith(".md") else rel


def resolve(target, basemap, nodes):
  """Resolve a link target (bundle path or bare name) to a concept id, or None."""
  t = target.strip().lstrip("/")
  if t.endswith(".md"):
    t = t[:-3]
  if t in nodes:
    return t
  return basemap.get(t.split("/")[-1])


def load_types():
  with open(TYPES_CONFIG, encoding="utf-8") as f:
    return json.load(f)


def build():
  nodes = {}
  docs = []  # (id, meta, body) kept for a second edge-resolution pass

  paths = (sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md")))
           + sorted(glob.glob(os.path.join(MEMORY_DIR, "*.md"))))
  for path in paths:
    if os.path.basename(path) in RESERVED:
      continue
    nid = concept_id(path)
    with open(path, encoding="utf-8") as f:
      meta, body = parse_frontmatter(f.read())
    tags = meta.get("tags", [])
    if isinstance(tags, str):
      tags = [tags]
    desc = meta.get("description", "")
    nodes[nid] = {
        "id": nid,
        "title": meta.get("title", os.path.basename(nid)),
        "type": meta.get("type", "note"),
        "description": desc,
        "tags": tags,
        "timestamp": meta.get("timestamp", ""),
        "resource": meta.get("resource", ""),
        "file": os.path.relpath(path, ROOT),
        "summary": desc or first_sentence(body),
    }
    docs.append((nid, meta, body))

  # basename -> concept id, preferring knowledge/ on collisions
  basemap = {}
  for nid in nodes:
    bn = nid.split("/")[-1]
    if bn not in basemap or nid.startswith("knowledge/"):
      basemap[bn] = nid

  edges = {}  # (src, tgt) -> type ; typed relations win over inline links
  for nid, meta, body in docs:
    # OKF standard markdown links: [text](/dir/concept.md)
    for m in MD_LINK.finditer(body):
      tgt = resolve(m.group(1), basemap, nodes)
      if tgt:
        edges.setdefault((nid, tgt), "links-to")
    # legacy [[wikilinks]] still tolerated (permissive consumer)
    for m in WIKILINK.finditer(body):
      tgt = resolve(m.group(1), basemap, nodes)
      if tgt:
        edges.setdefault((nid, tgt), "links-to")
    # typed relations (OKF extension): "target|type"
    for entry in meta.get("relations", []) or []:
      raw, _, etype = entry.partition("|")
      tgt = resolve(raw, basemap, nodes)
      if tgt:
        edges[(nid, tgt)] = etype.strip() or "related"

  edge_list = [
      {"source": s, "target": t, "type": ty}
      for (s, t), ty in edges.items()
      if s != t and t in nodes
  ]
  graph = {"nodes": list(nodes.values()), "edges": edge_list}

  types = load_types()
  with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(graph, f, indent=2, ensure_ascii=False)
  html = (HTML_TEMPLATE
          .replace("__GRAPH_DATA__", json.dumps(graph, ensure_ascii=False))
          .replace("__TYPES_DATA__", json.dumps(types, ensure_ascii=False)))
  with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)
  write_indexes(nodes, types)

  print(f"  nodes: {len(graph['nodes'])}  edges: {len(edge_list)}")
  print("  wrote: graph.json, graph.html, and OKF index.md files")


def write_indexes(nodes, types):
  """Generate OKF index.md per directory + a bundle-root index with version."""
  from collections import defaultdict
  by_dir = defaultdict(list)
  for d in DIR_DESC:  # seed known dirs so an emptied one still gets its index.md rewritten
    by_dir[d]
  for n in nodes.values():
    by_dir[os.path.dirname(n["file"])].append(n)
  # section header = plural-ish label from okf-types.json; unknown types fall back to
  # their own type string, title-cased, and sort after every configured type.
  type_labels = {t: meta["label"] + "s" for t, meta in types.items()}
  type_order = sorted(types, key=lambda t: types[t].get("order", 999))
  for d, items in by_dir.items():
    by_type = defaultdict(list)
    for n in items:
      by_type[n.get("type") or "note"].append(n)
    lines = [f"# {d.capitalize()}", ""]
    ordered = [t for t in type_order if t in by_type] + sorted(t for t in by_type if t not in type_order)
    for t in ordered:
      lines.append(f"## {type_labels.get(t, t.capitalize())}")
      lines.append("")
      for n in sorted(by_type[t], key=lambda n: n["id"]):
        desc = (n.get("description") or n.get("summary") or "").strip()
        date = (n.get("timestamp") or "")[:10]  # YYYY-MM-DD from the ISO timestamp
        entry = f"* [{n['title']}](/{n['file']})"
        if date:
          entry += f" — {date}"
        if desc:
          entry += f" — {desc}"
        lines.append(entry)
      lines.append("")
    with open(os.path.join(ROOT, d, "index.md"), "w", encoding="utf-8") as f:
      f.write("\n".join(lines).rstrip() + "\n")
  root = ["---", 'okf_version: "0.1"', "---", "",
          "# Knowledge Bundle", ""]
  for d in sorted(by_dir):
    line = f"* [{d}/]({d}/)"
    if DIR_DESC.get(d):
      line += f" - {DIR_DESC[d]}"
    root.append(line)
  with open(os.path.join(ROOT, "index.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(root) + "\n")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knowledge Graph</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0d1117;color:#c9d1d9;overflow:hidden}
  canvas{display:block;cursor:grab}
  canvas.grabbing{cursor:grabbing}
  #panel{position:fixed;top:16px;right:16px;width:300px;max-height:calc(100vh - 32px);overflow:auto;
    background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;font-size:13px;
    box-shadow:0 8px 24px rgba(0,0,0,.45);display:none}
  #panel h2{margin:0 0 6px;font-size:15px}
  #panel .type{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;color:#0d1117;font-weight:700;margin-bottom:8px}
  #panel .summary{color:#8b949e;line-height:1.5;margin:8px 0}
  #panel .tag{display:inline-block;background:#21262d;border:1px solid #30363d;border-radius:20px;padding:1px 8px;margin:2px 4px 0 0;font-size:11px;color:#8b949e}
  #panel a{color:#58a6ff;text-decoration:none;word-break:break-all}
  #panel ul{margin:6px 0;padding-left:18px}
  #panel li{margin:3px 0;cursor:pointer}
  #panel li:hover{color:#58a6ff}
  #legend{position:fixed;left:16px;bottom:16px;background:rgba(22,27,34,.85);border:1px solid #30363d;border-radius:10px;padding:10px 12px;font-size:12px}
  #legend .row{display:flex;align-items:center;margin:3px 0}
  #legend .dot{width:10px;height:10px;border-radius:50%;margin-right:8px}
  #hint{position:fixed;left:16px;top:16px;font-size:12px;color:#6e7681}
  #hint b{color:#8b949e}
  #search{position:fixed;top:16px;left:50%;transform:translateX(-50%);width:360px;z-index:10}
  #search input{width:100%;padding:8px 12px;border-radius:8px;border:1px solid #30363d;background:#161b22;
    color:#c9d1d9;font-size:13px;outline:none;box-shadow:0 8px 24px rgba(0,0,0,.35)}
  #search input:focus{border-color:#58a6ff}
  #searchResults{margin-top:6px;background:#161b22;border:1px solid #30363d;border-radius:8px;
    max-height:min(400px,calc(100vh - 70px));overflow:auto;display:none;box-shadow:0 8px 24px rgba(0,0,0,.45)}
  #searchResults .item{padding:8px 12px;cursor:pointer;font-size:13px;display:flex;justify-content:space-between;
    align-items:center;gap:8px;border-bottom:1px solid #21262d}
  #searchResults .item:last-child{border-bottom:none}
  #searchResults .item:hover{background:#21262d}
  #searchResults .item .t{color:#6e7681;font-size:11px;white-space:nowrap}
  #searchResults .empty{padding:8px 12px;color:#6e7681;font-size:12px}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="hint"><b>Knowledge Graph</b> &mdash; drag nodes &middot; scroll to zoom &middot; drag background to pan &middot; click a node for details</div>
<div id="search">
  <input id="searchInput" type="text" placeholder="Search nodes... (title, tag, id)" autocomplete="off">
  <div id="searchResults"></div>
</div>
<div id="legend"></div>
<div id="panel"></div>
<script>
const GRAPH = __GRAPH_DATA__;
const TYPES = __TYPES_DATA__;
const COLORS={};Object.keys(TYPES).forEach(t=>COLORS[t]=TYPES[t].color);
const LABELS={};Object.keys(TYPES).forEach(t=>LABELS[t]=TYPES[t].label);

const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
let W,H,DPR=Math.max(1,window.devicePixelRatio||1);
function resize(){W=innerWidth;H=innerHeight;canvas.width=W*DPR;canvas.height=H*DPR;canvas.style.width=W+'px';canvas.style.height=H+'px';ctx.setTransform(DPR,0,0,DPR,0,0)}
addEventListener('resize',resize);resize();

const nodes=GRAPH.nodes.map((n,i)=>({...n,x:W/2+Math.cos(i*2.4)*140+(Math.random()-.5)*40,y:H/2+Math.sin(i*2.4)*140+(Math.random()-.5)*40,vx:0,vy:0}));
const idx={};nodes.forEach(n=>idx[n.id]=n);
const edges=GRAPH.edges.filter(e=>idx[e.source]&&idx[e.target]).map(e=>({...e,s:idx[e.source],t:idx[e.target]}));
const deg={},adj={};nodes.forEach(n=>{deg[n.id]=0;adj[n.id]=new Set()});
edges.forEach(e=>{deg[e.source]++;deg[e.target]++;adj[e.source].add(e.target);adj[e.target].add(e.source)});
const rad=n=>7+Math.sqrt(deg[n.id]||0)*4;
const zr=()=>Math.min(1.6,Math.max(.7,scale));

let scale=1,ox=0,oy=0;
const toS=(x,y)=>[x*scale+ox,y*scale+oy];
const toW=(px,py)=>[(px-ox)/scale,(py-oy)/scale];

let alpha=1;
function step(){
  for(let i=0;i<nodes.length;i++){const a=nodes[i];
    for(let j=i+1;j<nodes.length;j++){const b=nodes[j];
      let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy;if(d2<1)d2=1;
      const d=Math.sqrt(d2),f=2600/d2,fx=dx/d*f,fy=dy/d*f;
      a.vx+=fx;a.vy+=fy;b.vx-=fx;b.vy-=fy}}
  edges.forEach(e=>{let dx=e.t.x-e.s.x,dy=e.t.y-e.s.y,d=Math.sqrt(dx*dx+dy*dy)||1,f=(d-95)*.02,fx=dx/d*f,fy=dy/d*f;
    e.s.vx+=fx;e.s.vy+=fy;e.t.vx-=fx;e.t.vy-=fy});
  nodes.forEach(n=>{n.vx+=(W/2-n.x)*.002;n.vy+=(H/2-n.y)*.002});
  nodes.forEach(n=>{if(n===dragNode)return;n.vx*=.85;n.vy*=.85;n.x+=n.vx*alpha;n.y+=n.vy*alpha});
  if(alpha>.005)alpha*=.99;
}

let hoverNode=null,selNode=null,dragNode=null,panning=false,lastX,lastY,downX,downY,moved=false;
function draw(){
  ctx.clearRect(0,0,W,H);
  const hl=selNode||hoverNode;
  const hset=hl?new Set([hl.id,...adj[hl.id]]):null;
  ctx.lineWidth=1;
  edges.forEach(e=>{
    const[x1,y1]=toS(e.s.x,e.s.y),[x2,y2]=toS(e.t.x,e.t.y);
    const active=hset&&(hl.id===e.source||hl.id===e.target);
    ctx.strokeStyle=active?'#58a6ff':'#30363d';
    ctx.globalAlpha=hset&&!active?.25:1;
    ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();
    if(active||scale>1.3){ctx.globalAlpha=active?1:.6;ctx.fillStyle='#8b949e';ctx.font='10px sans-serif';ctx.textAlign='center';
      ctx.fillText(e.type,(x1+x2)/2,(y1+y2)/2-2)}
  });
  ctx.globalAlpha=1;
  nodes.forEach(n=>{
    const[x,y]=toS(n.x,n.y),r=rad(n)*zr(),dim=hset&&!hset.has(n.id);
    ctx.globalAlpha=dim?.22:1;
    ctx.beginPath();ctx.arc(x,y,r,0,7);ctx.fillStyle=COLORS[n.type]||COLORS.note;ctx.fill();
    if(n===selNode){ctx.lineWidth=2.5;ctx.strokeStyle='#fff';ctx.stroke()}
    if(!dim&&(scale>.8||n===hl||(deg[n.id]||0)>=2)){
      ctx.fillStyle='#c9d1d9';ctx.font='12px sans-serif';ctx.textAlign='center';ctx.textBaseline='top';
      ctx.fillText(n.title,x,y+r+3)}
  });
  ctx.globalAlpha=1;
}
function loop(){step();draw();requestAnimationFrame(loop)}loop();

function nodeAt(px,py){for(let i=nodes.length-1;i>=0;i--){const n=nodes[i],[x,y]=toS(n.x,n.y),r=rad(n)*zr()+4;
  if((px-x)**2+(py-y)**2<=r*r)return n}return null}

canvas.addEventListener('mousedown',e=>{downX=lastX=e.clientX;downY=lastY=e.clientY;moved=false;
  const n=nodeAt(e.clientX,e.clientY);if(n){dragNode=n;alpha=Math.max(alpha,.5)}else{panning=true;canvas.classList.add('grabbing')}});
addEventListener('mousemove',e=>{
  if(Math.abs(e.clientX-downX)+Math.abs(e.clientY-downY)>3)moved=true;
  if(dragNode){const[wx,wy]=toW(e.clientX,e.clientY);dragNode.x=wx;dragNode.y=wy;dragNode.vx=dragNode.vy=0;alpha=Math.max(alpha,.3)}
  else if(panning){ox+=e.clientX-lastX;oy+=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY}
  else{const n=nodeAt(e.clientX,e.clientY);hoverNode=n;canvas.style.cursor=n?'pointer':'grab'}});
addEventListener('mouseup',e=>{
  if(!moved){const n=nodeAt(e.clientX,e.clientY);if(n){selNode=n;showPanel(n)}else{selNode=null;hide()}}
  dragNode=null;panning=false;canvas.classList.remove('grabbing')});
canvas.addEventListener('wheel',e=>{e.preventDefault();const f=e.deltaY<0?1.1:1/1.1,[wx,wy]=toW(e.clientX,e.clientY);
  scale=Math.min(4,Math.max(.2,scale*f));ox=e.clientX-wx*scale;oy=e.clientY-wy*scale},{passive:false});

const panel=document.getElementById('panel');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function etype(a,b){const e=edges.find(e=>(e.source===a&&e.target===b)||(e.source===b&&e.target===a));return e?e.type:'related'}
function showPanel(n){
  const c=COLORS[n.type]||COLORS.note,neigh=[...adj[n.id]];
  panel.innerHTML=
    '<h2>'+esc(n.title)+'</h2>'+
    '<span class="type" style="background:'+c+'">'+(LABELS[n.type]||esc(n.type))+'</span>'+
    (n.summary?'<div class="summary">'+esc(n.summary)+'</div>':'')+
    (n.tags&&n.tags.length?'<div>'+n.tags.map(t=>'<span class="tag">#'+esc(t)+'</span>').join('')+'</div>':'')+
    '<div style="margin-top:10px"><b>Connections ('+neigh.length+')</b><ul>'+
      neigh.map(id=>'<li data-id="'+id+'">'+esc(idx[id].title)+' <span style="color:#6e7681">&mdash; '+esc(etype(n.id,id))+'</span></li>').join('')+
    '</ul></div>'+
    (n.file?'<a href="'+encodeURI(n.file)+'" target="_blank">Open note &rarr; '+esc(n.file)+'</a>':'');
  panel.style.display='block';
  panel.querySelectorAll('li[data-id]').forEach(li=>li.onclick=()=>{const t=idx[li.dataset.id];selNode=t;showPanel(t);ox=W/2-t.x*scale;oy=H/2-t.y*scale});
}
function hide(){panel.style.display='none'}

function selectNode(n){
  selNode=n;showPanel(n);ox=W/2-n.x*scale;oy=H/2-n.y*scale;alpha=Math.max(alpha,.3);
  searchResults.style.display='none';searchInput.value=n.title;
}
const searchInput=document.getElementById('searchInput');
const searchResults=document.getElementById('searchResults');
function runSearch(){
  const q=searchInput.value.trim().toLowerCase();
  if(!q){searchResults.style.display='none';searchResults.innerHTML='';return}
  const hay=n=>[n.title,n.id,n.summary,...(n.tags||[])].join(' ').toLowerCase();
  const matches=nodes.filter(n=>hay(n).includes(q)).slice(0,25);
  searchResults.innerHTML=matches.length
    ? matches.map(n=>'<div class="item" data-id="'+esc(n.id)+'"><span>'+esc(n.title)+'</span><span class="t">'+esc(LABELS[n.type]||n.type)+'</span></div>').join('')
    : '<div class="empty">No matches</div>';
  searchResults.style.display='block';
  searchResults.querySelectorAll('.item').forEach(el=>el.onclick=()=>selectNode(idx[el.dataset.id]));
}
searchInput.addEventListener('input',runSearch);
searchInput.addEventListener('keydown',e=>{
  if(e.key==='Enter'){const first=searchResults.querySelector('.item');if(first)selectNode(idx[first.dataset.id])}
  if(e.key==='Escape'){searchInput.value='';searchResults.style.display='none';searchInput.blur()}
});
searchInput.addEventListener('focus',()=>{if(searchInput.value.trim())runSearch()});
document.addEventListener('click',e=>{if(!document.getElementById('search').contains(e.target))searchResults.style.display='none'});

const legend=document.getElementById('legend');
legend.innerHTML=[...new Set(nodes.map(n=>n.type))].map(t=>'<div class="row"><span class="dot" style="background:'+(COLORS[t]||COLORS.note)+'"></span>'+(LABELS[t]||t)+'</div>').join('');
</script>
</body>
</html>
"""


if __name__ == "__main__":
  build()
