#!/usr/bin/env python3
"""
Charlie Tracker — Multi-Project Spool Production Tracking
URL structure: / → /project/<id> → /project/<id>/spool/<spool_id>
"""
import os, sys, json
from datetime import datetime, date
from flask import Flask, render_template_string, request, jsonify, send_file, g

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'charlie-dev-key')
DATABASE_URL = os.environ.get('DATABASE_URL', '')
USE_PG = DATABASE_URL.startswith('postgres')

PRODUCTION_STEPS = [
    (1,"Material Receiving & Traceability","来料检验及可追溯性",5),
    (2,"Documentation Review (WPS/PQR/ITP)","文件审查（WPS/PQR/ITP）",3),
    (3,"Pipe Cutting — Dimensional Check","管道切割 — 尺寸检验",8),
    (4,"End Preparation / Bevelling","管口准备 / 坡口加工",5),
    (5,"Fit-Up & Assembly Inspection","组对及装配检验",10),
    (6,"Production Welding as per WPS","按WPS生产焊接",15),
    (7,"Visual Inspection (VT) — 100%","目视检验VT（全检）",8),
    (8,"Radiographic Test (RT) — 100%","射线检测RT（全检）★停止点",10),
    (9,"Magnetic Particle (MT) — 100%","磁粉检测MT（全检）",5),
    (10,"Cleaning Prior to Painting","涂装前清洁处理",3),
    (11,"Surface Preparation — Blasting","表面处理 — 喷砂",8),
    (12,"Painting Application","涂装施工（底漆/中间漆/面漆）",8),
    (13,"Coating Inspection — DFT","涂层检验 — 膜厚及附着力",4),
    (14,"Dimensional Inspection & Marking","尺寸检验及标识",5),
    (15,"Final Inspection — Released","最终检验 — 发货放行 ★见证",3),
]

# ── DB Layer ──────────────────────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        if USE_PG:
            import psycopg2, psycopg2.extras
            g.db = psycopg2.connect(DATABASE_URL.replace('postgres://','postgresql://',1), connect_timeout=10)
            g.db.autocommit = False; g.db_type = 'pg'
        else:
            import sqlite3
            g.db = sqlite3.connect(os.environ.get('SQLITE_PATH','tracker.db'))
            g.db.row_factory = sqlite3.Row; g.db_type = 'sqlite'
    return g.db

def db_execute(q, p=None):
    db = get_db()
    if g.db_type == 'pg':
        import psycopg2.extras
        q = q.replace('?','%s')
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(q, p or ()); return cur
    return db.execute(q, p or ())

def db_fetchall(q, p=None):
    cur = db_execute(q, p); rows = cur.fetchall()
    return rows if (USE_PG and g.db_type=='pg') else [dict(r) for r in rows]

def db_fetchone(q, p=None):
    cur = db_execute(q, p); r = cur.fetchone()
    return r if (r and USE_PG and g.db_type=='pg') else (dict(r) if r else None)

def db_commit(): get_db().commit()

@app.teardown_appcontext
def close_db(e):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    if USE_PG:
        import psycopg2
        c = psycopg2.connect(DATABASE_URL.replace('postgres://','postgresql://',1)); c.autocommit = True
        cur = c.cursor()
        # Drop old tables and recreate with new schema (multi-project)
        cur.execute("""
            DROP TABLE IF EXISTS activity_log;
            DROP TABLE IF EXISTS progress;
            DROP TABLE IF EXISTS spools;
            CREATE TABLE spools (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, spool_full TEXT DEFAULT '', iso_no TEXT DEFAULT '', marking TEXT DEFAULT '', mk_number TEXT DEFAULT '', main_diameter TEXT DEFAULT '', line TEXT DEFAULT '', sequence INTEGER DEFAULT 0, project TEXT DEFAULT '', created_at TIMESTAMP DEFAULT NOW(), UNIQUE(project, spool_id));
            CREATE TABLE progress (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER NOT NULL, completed INTEGER DEFAULT 0, completed_by TEXT DEFAULT '', completed_at TIMESTAMP, remarks TEXT DEFAULT '', UNIQUE(project, spool_id, step_number));
            CREATE TABLE activity_log (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER, action TEXT NOT NULL, operator TEXT DEFAULT '', timestamp TIMESTAMP DEFAULT NOW(), details TEXT DEFAULT '');
            CREATE INDEX idx_progress_ps ON progress(project, spool_id);
            CREATE INDEX idx_activity_ps ON activity_log(project, spool_id);
        """); c.close()
    else:
        import sqlite3
        c = sqlite3.connect(os.environ.get('SQLITE_PATH','tracker.db'))
        c.executescript("""
            CREATE TABLE IF NOT EXISTS spools (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, spool_full TEXT DEFAULT '', iso_no TEXT DEFAULT '', marking TEXT DEFAULT '', mk_number TEXT DEFAULT '', main_diameter TEXT DEFAULT '', line TEXT DEFAULT '', sequence INTEGER DEFAULT 0, project TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now')), UNIQUE(project, spool_id));
            CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER NOT NULL, completed INTEGER DEFAULT 0, completed_by TEXT DEFAULT '', completed_at TEXT, remarks TEXT DEFAULT '', UNIQUE(project, spool_id, step_number));
            CREATE TABLE IF NOT EXISTS activity_log (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER, action TEXT NOT NULL, operator TEXT DEFAULT '', timestamp TEXT DEFAULT (datetime('now')), details TEXT DEFAULT '');
        """); c.close()

# ── Helpers ───────────────────────────────────────────────────────────────────
def spool_progress(project, spool_id):
    rows = db_fetchall("SELECT step_number, completed FROM progress WHERE project=? AND spool_id=?", (project, spool_id))
    wm = {s[0]:s[3] for s in PRODUCTION_STEPS}; tw = sum(wm.values())
    cw = sum(wm.get(r['step_number'],0) for r in rows if r['completed'])
    return round(cw/tw*100, 1) if tw else 0.0

def project_stats(project):
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    st = {'total':len(spools),'completed':0,'in_progress':0,'not_started':0,'overall_pct':0.0,'by_diameter':{},'by_line':{}}
    tp = 0
    for s in spools:
        p = spool_progress(project, s['spool_id']); tp += p
        if p>=100: st['completed']+=1
        elif p>0: st['in_progress']+=1
        else: st['not_started']+=1
        d = s['main_diameter'] or '?'
        if d not in st['by_diameter']: st['by_diameter'][d] = {'total':0,'pct_sum':0}
        st['by_diameter'][d]['total']+=1; st['by_diameter'][d]['pct_sum']+=p
        l = s['line'] or '?'
        if l not in st['by_line']: st['by_line'][l] = {'total':0,'pct_sum':0}
        st['by_line'][l]['total']+=1; st['by_line'][l]['pct_sum']+=p
    if spools: st['overall_pct'] = round(tp/len(spools),1)
    for v in st['by_diameter'].values(): v['avg_pct'] = round(v['pct_sum']/v['total'],1) if v['total'] else 0
    for v in st['by_line'].values(): v['avg_pct'] = round(v['pct_sum']/v['total'],1) if v['total'] else 0
    return st

def fix_timestamps(rows):
    for r in rows:
        for k in ('completed_at','timestamp'):
            if r.get(k) and not isinstance(r[k], str): r[k] = str(r[k])
    return rows

# ── API: Projects ─────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/api/projects')
def api_projects():
    rows = db_fetchall("SELECT project, COUNT(*) as spool_count FROM spools GROUP BY project ORDER BY project")
    result = []
    for r in rows:
        p = r['project']
        st = project_stats(p)
        result.append({'project': p, 'spool_count': r['spool_count'], 'overall_pct': st['overall_pct'],
                        'completed': st['completed'], 'in_progress': st['in_progress'], 'not_started': st['not_started']})
    return jsonify(result)

# ── API: Project Dashboard ────────────────────────────────────────────────────
@app.route('/project/<project>')
def project_page(project):
    return render_template_string(PROJECT_HTML, project=project)

@app.route('/api/project/<project>/dashboard')
def api_project_dashboard(project):
    st = project_stats(project)
    act = db_fetchall("SELECT * FROM activity_log WHERE project=? ORDER BY timestamp DESC LIMIT 20", (project,))
    st['recent_activity'] = fix_timestamps(act)
    return jsonify(st)

@app.route('/api/project/<project>/spools')
def api_project_spools(project):
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    result = []
    for s in spools:
        p = spool_progress(project, s['spool_id'])
        result.append({'spool': s, 'progress_pct': p})
    return jsonify(result)

# ── API: Spool Detail ─────────────────────────────────────────────────────────
@app.route('/project/<project>/spool/<spool_id>')
def spool_page(project, spool_id):
    return render_template_string(SPOOL_HTML, project=project, spool_id=spool_id)

@app.route('/api/project/<project>/spool/<spool_id>')
def api_spool(project, spool_id):
    sp = db_fetchone("SELECT * FROM spools WHERE project=? AND spool_id=?", (project, spool_id))
    if not sp: return jsonify({'error':'Not found'}), 404
    steps = fix_timestamps(db_fetchall("SELECT * FROM progress WHERE project=? AND spool_id=? ORDER BY step_number", (project, spool_id)))
    act = fix_timestamps(db_fetchall("SELECT * FROM activity_log WHERE project=? AND spool_id=? ORDER BY timestamp DESC LIMIT 10", (project, spool_id)))
    return jsonify({'spool':sp, 'progress_pct': spool_progress(project, spool_id), 'steps':steps, 'activity':act,
        'step_definitions':[{'number':s[0],'name_en':s[1],'name_cn':s[2],'weight':s[3]} for s in PRODUCTION_STEPS]})

@app.route('/api/project/<project>/spool/<spool_id>/step/<int:step>', methods=['POST'])
def api_update_step(project, spool_id, step):
    d = request.get_json() or {}
    comp = 1 if d.get('completed') else 0
    op = d.get('operator',''); rem = d.get('remarks','')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if USE_PG:
        db_execute("INSERT INTO progress (project,spool_id,step_number,completed,completed_by,completed_at,remarks) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (project,spool_id,step_number) DO UPDATE SET completed=EXCLUDED.completed, completed_by=EXCLUDED.completed_by, completed_at=CASE WHEN EXCLUDED.completed=1 THEN EXCLUDED.completed_at ELSE NULL END, remarks=EXCLUDED.remarks",
            (project, spool_id, step, comp, op, now if comp else None, rem))
    else:
        db_execute("INSERT INTO progress (project,spool_id,step_number,completed,completed_by,completed_at,remarks) VALUES (?,?,?,?,?,?,?) ON CONFLICT(project,spool_id,step_number) DO UPDATE SET completed=excluded.completed, completed_by=excluded.completed_by, completed_at=CASE WHEN excluded.completed=1 THEN excluded.completed_at ELSE NULL END, remarks=excluded.remarks",
            (project, spool_id, step, comp, op, now if comp else None, rem))
    sn = next((s[1] for s in PRODUCTION_STEPS if s[0]==step), f"Step {step}")
    act = "completed" if comp else "unchecked"
    db_execute("INSERT INTO activity_log (project,spool_id,step_number,action,operator,details) VALUES (?,?,?,?,?,?)",
        (project, spool_id, step, act, op, f"{sn}: {act} by {op}"))
    db_commit()
    return jsonify({'ok':True, 'progress_pct': spool_progress(project, spool_id)})

# ── API: Import & Export ──────────────────────────────────────────────────────
@app.route('/api/import', methods=['POST'])
def api_import():
    data = request.get_json()
    if not data or not isinstance(data, list): return jsonify({'error':'Expected JSON array'}), 400
    count = 0
    for s in data:
        proj = s.get('project','')
        try:
            if USE_PG:
                db_execute("INSERT INTO spools (project,spool_id,spool_full,iso_no,marking,mk_number,main_diameter,line,sequence) VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT (project,spool_id) DO NOTHING",
                    (proj, s['spool_id'], s.get('spool_full',''), s.get('iso_no',''), s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''), s.get('line',''), s.get('sequence',0)))
            else:
                db_execute("INSERT OR IGNORE INTO spools (project,spool_id,spool_full,iso_no,marking,mk_number,main_diameter,line,sequence) VALUES (?,?,?,?,?,?,?,?,?)",
                    (proj, s['spool_id'], s.get('spool_full',''), s.get('iso_no',''), s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''), s.get('line',''), s.get('sequence',0)))
            for sn,_,_,_ in PRODUCTION_STEPS:
                if USE_PG:
                    db_execute("INSERT INTO progress (project,spool_id,step_number,completed) VALUES (?,?,?,0) ON CONFLICT (project,spool_id,step_number) DO NOTHING", (proj, s['spool_id'], sn))
                else:
                    db_execute("INSERT OR IGNORE INTO progress (project,spool_id,step_number,completed) VALUES (?,?,?,0)", (proj, s['spool_id'], sn))
            count += 1
        except Exception as e: print(f"Import error {s.get('spool_id','?')}: {e}")
    db_commit()
    return jsonify({'ok':True, 'imported':count})

@app.route('/api/project/<project>/export')
def api_export(project):
    import openpyxl; from openpyxl.styles import Font, PatternFill, Alignment; import tempfile
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = project
    hdr = ['#','Spool','Diameter','Line','Progress %'] + [f"S{s[0]}" for s in PRODUCTION_STEPS]
    hf = Font(bold=True,size=9,color='FFFFFF'); hfill = PatternFill(start_color='2F5496',end_color='2F5496',fill_type='solid')
    for c,h in enumerate(hdr,1):
        cl = ws.cell(1,c,h); cl.font=hf; cl.fill=hfill; cl.alignment=Alignment(horizontal='center',wrap_text=True)
    for i,s in enumerate(spools,2):
        p = spool_progress(project, s['spool_id'])
        steps = db_fetchall("SELECT step_number,completed FROM progress WHERE project=? AND spool_id=?", (project, s['spool_id']))
        sm = {st['step_number']:st['completed'] for st in steps}
        ws.cell(i,1,i-1); ws.cell(i,2,s['spool_id']); ws.cell(i,3,s['main_diameter']); ws.cell(i,4,s['line']); ws.cell(i,5,p)
        for j,sd in enumerate(PRODUCTION_STEPS):
            c = 6+j; done = sm.get(sd[0],0)
            ws.cell(i,c,'\u2713' if done else '')
            if done: ws.cell(i,c).fill = PatternFill(start_color='C6EFCE',end_color='C6EFCE',fill_type='solid')
    ws.column_dimensions['B'].width=15; ws.freeze_panes='A2'
    tmp = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False); wb.save(tmp.name)
    return send_file(tmp.name, as_attachment=True, download_name=f"{project}_progress_{date.today().strftime('%Y%m%d')}.xlsx")

@app.route('/healthz')
def healthz():
    try: db_execute("SELECT 1"); return jsonify({'status':'ok','db':'connected'})
    except Exception as e: return jsonify({'status':'error','db':str(e)}), 500

# ── HTML: Home (Project List) ─────────────────────────────────────────────────
COMMON_CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#333}
.header{background:linear-gradient(135deg,#2F5496,#1a3a6e);color:#fff;padding:16px 20px}
.header h1{font-size:20px}.header .sub{font-size:12px;opacity:.8;margin-top:4px}
.back{color:#fff;text-decoration:none;font-size:13px;opacity:.8}.back:hover{opacity:1}
.pbar-bg{background:#e8e8e8;border-radius:8px;height:12px;overflow:hidden}
.pbar-fill{height:100%;border-radius:8px;transition:width .5s}
.pct-green{color:#27ae60}.pct-yellow{color:#f39c12}.pct-red{color:#e74c3c}.pct-blue{color:#2F5496}
.btn{background:#2F5496;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px;text-decoration:none;display:inline-block}
.btn:hover{background:#1a3a6e}
.line-badge{display:inline-block;width:22px;height:22px;border-radius:50%;color:#fff;text-align:center;line-height:22px;font-size:11px;font-weight:700}
.line-A{background:#2d8a4e}.line-B{background:#2F5496}.line-C{background:#c0392b}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;padding:16px}
.stat-card{background:#fff;border-radius:10px;padding:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.stat-card .value{font-size:28px;font-weight:700;color:#2F5496}.stat-card .label{font-size:11px;color:#888;margin-top:4px}
@media(max-width:600px){.stats-grid{grid-template-columns:repeat(2,1fr)}}"""

HOME_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ENERXON Tracker</title><style>""" + COMMON_CSS + """
.proj-list{padding:16px;display:grid;gap:12px}
.proj-card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);cursor:pointer;transition:transform .15s}
.proj-card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.12)}
.proj-card .id{font-size:20px;font-weight:700;color:#2F5496}.proj-card .count{font-size:13px;color:#888;margin-top:4px}
.proj-card .stats{display:flex;gap:16px;margin-top:12px;font-size:12px}
.proj-card .stats span{padding:3px 8px;border-radius:4px}
.proj-card .done{background:#e8f5e9;color:#27ae60}.proj-card .wip{background:#fff3e0;color:#f39c12}.proj-card .todo{background:#fce4ec;color:#e74c3c}
.empty{text-align:center;padding:60px 20px;color:#888;font-size:16px}
</style></head><body>
<div class="header"><h1>ENERXON Production Tracker</h1><div class="sub">生产进度追踪系统 — Select a project / 选择项目</div></div>
<div class="proj-list" id="projects"><div class="empty">Loading projects... / 加载中...</div></div>
<script>
async function load(){
  const r = await fetch('/api/projects'); const projects = await r.json();
  if(!projects.length){ document.getElementById('projects').innerHTML='<div class="empty">No projects yet / 暂无项目<br><br>Use the API to import spools:<br><code>POST /api/import</code></div>'; return; }
  document.getElementById('projects').innerHTML = projects.map(p => `
    <div class="proj-card" onclick="location.href='/project/${p.project}'">
      <div class="id">${p.project}</div>
      <div class="count">${p.spool_count} spools</div>
      <div class="pbar-bg" style="margin-top:10px"><div class="pbar-fill" style="width:${p.overall_pct}%;background:${p.overall_pct>=100?'#27ae60':'#2F5496'}"></div></div>
      <div style="font-size:14px;font-weight:700;margin-top:6px;color:#2F5496">${p.overall_pct}%</div>
      <div class="stats">
        <span class="done">${p.completed} done</span>
        <span class="wip">${p.in_progress} in progress</span>
        <span class="todo">${p.not_started} pending</span>
      </div>
    </div>`).join('');
}
load(); setInterval(load, 30000);
</script></body></html>"""

# ── HTML: Project Dashboard ───────────────────────────────────────────────────
PROJECT_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ project }} — Tracker</title><style>""" + COMMON_CSS + """
.section{padding:0 16px 16px}.section h2{font-size:16px;color:#2F5496;margin:16px 0 8px}
.toolbar{display:flex;gap:8px;padding:8px 16px;flex-wrap:wrap}
.toolbar input,.toolbar select{padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px}
.toolbar input{flex:1;min-width:150px}
.spool-list{display:grid;gap:8px}
.spool-row{background:#fff;border-radius:8px;padding:12px 16px;display:flex;align-items:center;gap:12px;box-shadow:0 1px 2px rgba(0,0,0,.05);cursor:pointer;transition:transform .1s}
.spool-row:active{transform:scale(.99)}
.spool-row .info{flex:1;min-width:0}.spool-row .name{font-weight:600;font-size:14px}.spool-row .meta{font-size:11px;color:#888}
.spool-row .pct{font-size:18px;font-weight:700;min-width:55px;text-align:right}
.spool-row .bar{width:80px;min-width:80px}
.diam-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px}
.diam-card{background:#fff;border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.diam-card .d{font-size:20px;font-weight:700;color:#2F5496}.diam-card .p{font-size:13px;margin-top:4px}
.activity-item{font-size:12px;padding:6px 0;border-bottom:1px solid #f0f0f0;color:#666}
@media(max-width:600px){.spool-row .bar{display:none}}
</style></head><body>
<div class="header">
  <a class="back" href="/">← All Projects / 所有项目</a>
  <h1>{{ project }}</h1>
  <div class="sub">Production Progress / 生产进度</div>
</div>
<div class="stats-grid" id="stats"></div>
<div class="section"><h2>By Diameter / 按管径</h2><div class="diam-grid" id="diam"></div></div>
<div class="toolbar">
  <input type="text" id="q" placeholder="Search spool / 搜索管段..." oninput="filter()">
  <select id="fl" onchange="filter()"><option value="">All Lines</option><option value="A">Line A</option><option value="B">Line B</option><option value="C">Line C</option></select>
  <select id="fs" onchange="filter()"><option value="">All Status</option><option value="done">Done</option><option value="wip">In Progress</option><option value="todo">Not Started</option></select>
  <a class="btn" href="/api/project/{{ project }}/export">Export Excel</a>
</div>
<div class="section"><div class="spool-list" id="list"></div></div>
<div class="section" id="act"></div>
<script>
const P='{{project}}'; let all=[];
async function load(){
  const[dr,sr]=await Promise.all([fetch(`/api/project/${P}/dashboard`),fetch(`/api/project/${P}/spools`)]);
  const st=await dr.json(); all=await sr.json();
  document.getElementById('stats').innerHTML=`
    <div class="stat-card"><div class="value">${st.total}</div><div class="label">Total / 总数</div></div>
    <div class="stat-card"><div class="value pct-blue">${st.overall_pct}%</div><div class="label">Progress / 进度</div>
      <div class="pbar-bg" style="margin-top:8px"><div class="pbar-fill" style="width:${st.overall_pct}%;background:#2F5496"></div></div></div>
    <div class="stat-card"><div class="value pct-green">${st.completed}</div><div class="label">Done / 完成</div></div>
    <div class="stat-card"><div class="value pct-yellow">${st.in_progress}</div><div class="label">WIP / 进行中</div></div>
    <div class="stat-card"><div class="value pct-red">${st.not_started}</div><div class="label">Pending / 待开始</div></div>`;
  const ds=Object.entries(st.by_diameter).sort((a,b)=>(parseInt(b[0])||0)-(parseInt(a[0])||0));
  document.getElementById('diam').innerHTML=ds.map(([d,v])=>`<div class="diam-card"><div class="d">${d}</div><div class="p">${v.total} spools</div>
    <div class="pbar-bg" style="margin-top:6px"><div class="pbar-fill" style="width:${v.avg_pct}%;background:${v.avg_pct>=100?'#27ae60':'#2F5496'}"></div></div>
    <div style="font-size:12px;margin-top:4px;font-weight:600">${v.avg_pct}%</div></div>`).join('');
  render(all);
  if(st.recent_activity&&st.recent_activity.length)
    document.getElementById('act').innerHTML='<h2 style="font-size:16px;color:#2F5496;margin:8px 0">Recent / 最近动态</h2>'+
      st.recent_activity.slice(0,10).map(a=>`<div class="activity-item"><strong>${a.spool_id}</strong> — ${a.details||a.action} <span style="color:#aaa;font-size:11px">${a.timestamp||''}</span></div>`).join('');
}
function render(sp){
  document.getElementById('list').innerHTML=sp.map(s=>{
    const p=s.progress_pct,c=p>=100?'pct-green':p>0?'pct-yellow':'pct-red',bg=p>=100?'#27ae60':p>0?'#f39c12':'#e8e8e8',l=s.spool.line||'?';
    return`<div class="spool-row" onclick="location.href='/project/${P}/spool/${s.spool.spool_id}'">
      <span class="line-badge line-${l}">${l}</span>
      <div class="info"><div class="name">${s.spool.spool_id}</div><div class="meta">${s.spool.main_diameter||''} · ${s.spool.iso_no||''}</div></div>
      <div class="bar"><div class="pbar-bg"><div class="pbar-fill" style="width:${p}%;background:${bg}"></div></div></div>
      <div class="pct ${c}">${p}%</div></div>`;}).join('');
}
function filter(){
  const q=document.getElementById('q').value.toLowerCase(),l=document.getElementById('fl').value,s=document.getElementById('fs').value;
  render(all.filter(x=>{
    if(q&&!x.spool.spool_id.toLowerCase().includes(q)&&!(x.spool.iso_no||'').toLowerCase().includes(q))return false;
    if(l&&x.spool.line!==l)return false;
    if(s==='done'&&x.progress_pct<100)return false;
    if(s==='wip'&&(x.progress_pct<=0||x.progress_pct>=100))return false;
    if(s==='todo'&&x.progress_pct>0)return false;
    return true;
  }));
}
load(); setInterval(load,30000);
</script></body></html>"""

# ── HTML: Spool Detail ────────────────────────────────────────────────────────
SPOOL_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ spool_id }} — Checklist</title><style>""" + COMMON_CSS + """
.info-bar{background:#fff;padding:12px 16px;display:flex;flex-wrap:wrap;gap:16px;align-items:center;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.info-item{font-size:12px}.info-item .lb{color:#888}.info-item .vl{font-weight:600}
.prog{text-align:center;padding:20px}.prog .big{font-size:48px;font-weight:700;color:#2F5496}.prog .lbl{font-size:13px;color:#888}
.op-input{padding:8px 16px}.op-input input{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px}
.checklist{padding:8px 16px 80px}
.step{background:#fff;border-radius:10px;margin-bottom:8px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.step.done{border-left:4px solid #27ae60}.step.pending{border-left:4px solid #e8e8e8}
.step-h{display:flex;align-items:center;padding:14px 16px;gap:12px;cursor:pointer}
.step-h .num{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0}
.step.done .num{background:#27ae60;color:#fff}.step.pending .num{background:#e8e8e8;color:#888}
.step-h .text{flex:1}.step-h .en{font-size:13px;font-weight:600}.step-h .cn{font-size:11px;color:#888}
.step-h .chk{font-size:24px}
.step-meta{padding:0 16px 8px 56px;font-size:11px;color:#888}
.step-rem{padding:4px 16px 12px 56px}
.step-rem input{width:100%;padding:6px 10px;border:1px solid #ddd;border-radius:6px;font-size:12px}
.wbadge{font-size:10px;background:#f0f2f5;padding:2px 6px;border-radius:4px;color:#888}
</style></head><body>
<div class="header">
  <a class="back" href="/project/{{ project }}">← {{ project }}</a>
  <h1>{{ spool_id }}</h1><div class="sub" id="ss"></div>
</div>
<div class="info-bar" id="ib"></div>
<div class="prog"><div class="big" id="bp">0%</div><div class="lbl">Production Progress / 生产进度</div></div>
<div class="pbar-bg" style="margin:0 16px"><div class="pbar-fill" id="mb" style="width:0%"></div></div>
<div class="op-input"><input type="text" id="op" placeholder="Your name / 你的姓名"></div>
<div class="checklist" id="cl"></div>
<script>
const P='{{project}}',SID='{{spool_id}}'; let D;
async function load(){
  const r=await fetch(`/api/project/${P}/spool/${SID}`); D=await r.json(); render();
}
function render(){
  const s=D.spool, p=D.progress_pct;
  document.getElementById('ss').textContent=`${s.main_diameter} · Line ${s.line} · ${s.iso_no||''}`;
  document.getElementById('bp').textContent=p+'%';
  document.getElementById('bp').style.color=p>=100?'#27ae60':p>0?'#2F5496':'#e74c3c';
  document.getElementById('mb').style.width=p+'%';
  document.getElementById('mb').style.background=p>=100?'#27ae60':'#2F5496';
  document.getElementById('ib').innerHTML=`
    <span class="line-badge line-${s.line}">${s.line}</span>
    <div class="info-item"><span class="lb">Diameter:</span> <span class="vl">${s.main_diameter}</span></div>
    <div class="info-item"><span class="lb">ISO:</span> <span class="vl">${s.iso_no||'-'}</span></div>
    <div class="info-item"><span class="lb">MK:</span> <span class="vl">${s.mk_number||'-'}</span></div>`;
  const sm={}; D.steps.forEach(x=>{sm[x.step_number]=x});
  document.getElementById('cl').innerHTML=D.step_definitions.map(d=>{
    const st=sm[d.number]||{}, dn=!!st.completed;
    return`<div class="step ${dn?'done':'pending'}" id="s${d.number}">
      <div class="step-h" onclick="tog(${d.number},${!dn})">
        <div class="num">${d.number}</div>
        <div class="text"><div class="en">${d.name_en} <span class="wbadge">${d.weight}%</span></div><div class="cn">${d.name_cn}</div></div>
        <div class="chk">${dn?'\u2705':'\u2b1c'}</div>
      </div>
      ${dn&&st.completed_by?`<div class="step-meta">\u2713 ${st.completed_by} · ${st.completed_at||''}</div>`:''}
      <div class="step-rem"><input type="text" placeholder="Remarks / 备注" value="${st.remarks||''}" onchange="rem(${d.number},this.value)" onclick="event.stopPropagation()"></div>
    </div>`;}).join('');
}
async function tog(n,c){
  const op=document.getElementById('op').value||'Unknown';
  const ri=document.querySelector(`#s${n} .step-rem input`);
  await fetch(`/api/project/${P}/spool/${SID}/step/${n}`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({completed:c,operator:op,remarks:ri?ri.value:''})}); await load();
}
async function rem(n,v){
  const sm={}; D.steps.forEach(x=>{sm[x.step_number]=x}); const st=sm[n]||{};
  await fetch(`/api/project/${P}/spool/${SID}/step/${n}`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({completed:!!st.completed,operator:st.completed_by||document.getElementById('op').value||'',remarks:v})});
}
load();
</script></body></html>"""

# ── Init & Run ────────────────────────────────────────────────────────────────
try: init_db(); print("DB initialized")
except Exception as e: print(f"DB init: {e}")

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST','0.0.0.0'), port=int(os.environ.get('PORT',5000)))
