#!/usr/bin/env python3
"""
Charlie Tracker — Multi-Project Spool Production Tracking
URL structure: / → /project/<id> → /project/<id>/spool/<spool_id>
"""
import os, sys, json
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template_string, request, jsonify, send_file, g, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'charlie-dev-key')
DATABASE_URL = os.environ.get('DATABASE_URL', '')
USE_PG = DATABASE_URL.startswith('postgres')
SITE_PASSWORD = os.environ.get('SITE_PASSWORD', 'Enerxon@china')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Not authenticated'}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        pw = request.form.get('password', '')
        if pw == SITE_PASSWORD:
            session['authenticated'] = True
            session.permanent = True
            app.permanent_session_lifetime = __import__('datetime').timedelta(days=90)
            return redirect('/')
        error = 'Wrong password / \u5bc6\u7801\u9519\u8bef'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ENERXON Tracker — Login</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;display:flex;align-items:center;justify-content:center;min-height:100vh}
.login-box{background:#fff;border-radius:16px;padding:40px;width:320px;box-shadow:0 4px 20px rgba(0,0,0,0.1);text-align:center}
.login-box h1{color:#2F5496;font-size:20px;margin-bottom:4px}
.login-box .cn{color:#888;font-size:13px;margin-bottom:24px}
.login-box input{width:100%;padding:12px;border:2px solid #ddd;border-radius:8px;font-size:16px;margin-bottom:16px;text-align:center}
.login-box input:focus{border-color:#2F5496;outline:none}
.login-box button{width:100%;padding:12px;background:#2F5496;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer}
.login-box button:hover{background:#1a3a6e}
.error{color:#e74c3c;font-size:13px;margin-bottom:12px}
</style></head><body>
<div class="login-box">
  <h1>ENERXON Tracker</h1>
  <div class="cn">\u751f\u4ea7\u8fdb\u5ea6\u8ffd\u8e2a\u7cfb\u7edf</div>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST">
    <input type="password" name="password" placeholder="Password / \u5bc6\u7801" autofocus>
    <button type="submit">Enter / \u8fdb\u5165</button>
  </form>
</div>
</body></html>"""

PRODUCTION_STEPS = [
    (1,"Material Receiving & Traceability","来料检验及可追溯性",5),
    (2,"Documentation Review (WPS/PQR/ITP)","文件审查（WPS/PQR/ITP）",3),
    (3,"Pipe Cutting — Dimensional Check","管道切割 — 尺寸检验",8),
    (4,"End Preparation / Bevelling","管口准备 / 坡口加工",5),
    (5,"Fit-Up & Assembly Inspection","组对及装配检验",10),
    (16,"Branch Welding","支管焊接",5),
    (6,"Production Welding as per WPS","按WPS主管焊接",10),
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

# Production rate estimates (spools per day by diameter) — same as charlie_gantt.py
SPOOLS_PER_DAY = {'32':1.5,'24':1.7,'18':3.0,'16':2.0,'8':1.5,'2':2.5,'1':2.5}
PAINTING_DAYS = 13
DIAMETER_ORDER = ['32','24','18','16','8','2','1']

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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS spools (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, spool_full TEXT DEFAULT '', iso_no TEXT DEFAULT '', marking TEXT DEFAULT '', mk_number TEXT DEFAULT '', main_diameter TEXT DEFAULT '', line TEXT DEFAULT '', sequence INTEGER DEFAULT 0, project TEXT DEFAULT '', has_branches INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT NOW(), UNIQUE(project, spool_id));
            CREATE TABLE progress (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER NOT NULL, completed INTEGER DEFAULT 0, completed_by TEXT DEFAULT '', completed_at TIMESTAMP, remarks TEXT DEFAULT '', UNIQUE(project, spool_id, step_number));
            CREATE TABLE activity_log (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER, action TEXT NOT NULL, operator TEXT DEFAULT '', timestamp TIMESTAMP DEFAULT NOW(), details TEXT DEFAULT '');
            CREATE INDEX idx_progress_ps ON progress(project, spool_id);
            CREATE INDEX idx_activity_ps ON activity_log(project, spool_id);
            CREATE TABLE IF NOT EXISTS schedule (id SERIAL PRIMARY KEY, project TEXT NOT NULL, diameter TEXT NOT NULL, task_type TEXT NOT NULL, description TEXT DEFAULT '', planned_start DATE NOT NULL, planned_end DATE NOT NULL, spool_count INTEGER DEFAULT 0, UNIQUE(project, diameter, task_type));
        """); c.close()
    else:
        import sqlite3
        c = sqlite3.connect(os.environ.get('SQLITE_PATH','tracker.db'))
        c.executescript("""
            CREATE TABLE IF NOT EXISTS spools (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, spool_full TEXT DEFAULT '', iso_no TEXT DEFAULT '', marking TEXT DEFAULT '', mk_number TEXT DEFAULT '', main_diameter TEXT DEFAULT '', line TEXT DEFAULT '', sequence INTEGER DEFAULT 0, project TEXT DEFAULT '', has_branches INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), UNIQUE(project, spool_id));
            CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER NOT NULL, completed INTEGER DEFAULT 0, completed_by TEXT DEFAULT '', completed_at TEXT, remarks TEXT DEFAULT '', UNIQUE(project, spool_id, step_number));
            CREATE TABLE IF NOT EXISTS activity_log (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER, action TEXT NOT NULL, operator TEXT DEFAULT '', timestamp TEXT DEFAULT (datetime('now')), details TEXT DEFAULT '');
            CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, diameter TEXT NOT NULL, task_type TEXT NOT NULL, description TEXT DEFAULT '', planned_start TEXT NOT NULL, planned_end TEXT NOT NULL, spool_count INTEGER DEFAULT 0, UNIQUE(project, diameter, task_type));
        """); c.close()

# ── Helpers ───────────────────────────────────────────────────────────────────
def spool_progress(project, spool_id):
    rows = db_fetchall("SELECT step_number, completed FROM progress WHERE project=? AND spool_id=?", (project, spool_id))
    sp = db_fetchone("SELECT has_branches FROM spools WHERE project=? AND spool_id=?", (project, spool_id))
    has_br = sp and sp.get('has_branches')
    wm = {s[0]:s[3] for s in PRODUCTION_STEPS if s[0] != 16 or has_br}
    tw = sum(wm.values())
    cw = sum(wm.get(r['step_number'],0) for r in rows if r['completed'] and r['step_number'] in wm)
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

def parse_date(val):
    """Parse date from various formats (ISO, PG timestamp, HTTP date)."""
    if not val: return None
    s = str(val).strip()[:10]
    try: return date.fromisoformat(s)
    except: pass
    # Try parsing "Wed, 11 Mar 2026 00:00:00 GMT" etc.
    for fmt in ('%a, %d %b %Y', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
        try: return datetime.strptime(str(val).strip()[:30], fmt + '%f' if '.' in str(val) else fmt).date()
        except: pass
    try: return datetime.strptime(str(val).strip().split('.')[0].split('+')[0], '%Y-%m-%d %H:%M:%S').date()
    except: pass
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(str(val)).date()
    except: pass
    return None

def schedule_status(project):
    """Calculate on-track/danger/delay status per diameter based on schedule vs actual progress."""
    sched = db_fetchall("SELECT * FROM schedule WHERE project=? ORDER BY planned_start", (project,))
    if not sched:
        return None
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    today = date.today()
    # Group spools by diameter
    by_diam = {}
    for s in spools:
        d = s['main_diameter'] or '?'
        if d not in by_diam: by_diam[d] = []
        by_diam[d].append(s)
    # Build schedule map: diameter -> {fabrication: {start, end}, painting: {start, end}}
    sched_map = {}
    for sc in sched:
        d = sc['diameter']
        if d not in sched_map: sched_map[d] = {}
        sd = parse_date(sc['planned_start']); ed = parse_date(sc['planned_end'])
        sched_map[d][sc['task_type']] = {'start': str(sd) if sd else '', 'end': str(ed) if ed else '', 'spool_count': sc.get('spool_count',0), 'description': sc.get('description','')}
    result = []
    overall_expected = 0; overall_actual = 0; overall_count = 0
    for diam in DIAMETER_ORDER:
        dk = f'{diam}"'
        if dk not in sched_map and diam not in sched_map: continue
        sm = sched_map.get(dk, sched_map.get(diam, {}))
        fab = sm.get('fabrication', sm.get('Fabricacion', {}))
        paint = sm.get('painting', sm.get('Pintura', {}))
        if not fab: continue
        try:
            fab_start = parse_date(fab['start']); fab_end = parse_date(fab['end'])
            if not fab_start or not fab_end: continue
            if paint:
                paint_start = parse_date(paint['start']); paint_end = parse_date(paint['end'])
                total_end = paint_end if paint_end else fab_end
            else:
                total_end = fab_end
            total_days = max(1, (total_end - fab_start).days)
            elapsed = max(0, min((today - fab_start).days, total_days))
            expected_pct = round(elapsed / total_days * 100, 1) if total_days > 0 else 0
        except: continue
        # Actual progress for this diameter
        diam_spools = by_diam.get(dk, by_diam.get(f'{diam}\"', []))
        if not diam_spools: continue
        actual_sum = sum(spool_progress(project, s['spool_id']) for s in diam_spools)
        actual_pct = round(actual_sum / len(diam_spools), 1)
        diff = actual_pct - expected_pct
        if today < fab_start:
            status = 'not_started'
        elif diff >= -5:
            status = 'on_time'  # Green
        elif diff >= -15:
            status = 'at_risk'  # Orange
        else:
            status = 'delayed'  # Red
        overall_expected += expected_pct; overall_actual += actual_pct; overall_count += 1
        result.append({
            'diameter': dk, 'spool_count': len(diam_spools),
            'expected_pct': expected_pct, 'actual_pct': actual_pct, 'diff': round(diff, 1), 'status': status,
            'fab_start': fab.get('start',''), 'fab_end': fab.get('end',''),
            'paint_start': paint.get('start','') if paint else '', 'paint_end': paint.get('end','') if paint else '',
            'total_start': fab.get('start',''), 'total_end': str(total_end),
        })
    overall_status = 'on_time'
    if overall_count > 0:
        avg_diff = (overall_actual - overall_expected) / overall_count
        if avg_diff < -15: overall_status = 'delayed'
        elif avg_diff < -5: overall_status = 'at_risk'
    return {'diameters': result, 'overall_status': overall_status, 'today': str(today)}

def daily_activity(project, day=None):
    """Get activity for a specific day."""
    if not day: day = date.today().strftime('%Y-%m-%d')
    if USE_PG:
        rows = db_fetchall("SELECT * FROM activity_log WHERE project=? AND timestamp::date = ?::date ORDER BY timestamp DESC", (project, day))
    else:
        rows = db_fetchall("SELECT * FROM activity_log WHERE project=? AND timestamp LIKE ? ORDER BY timestamp DESC", (project, f"{day}%"))
    return fix_timestamps(rows)

def generate_report_data(project):
    """Build full report data for a project."""
    st = project_stats(project)
    sched = schedule_status(project)
    today = date.today().strftime('%Y-%m-%d')
    today_act = daily_activity(project, today)
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    # Count steps completed today
    steps_today = len([a for a in today_act if a.get('action') == 'completed'])
    # Spools completed (100%)
    completed_spools = []
    for s in spools:
        p = spool_progress(project, s['spool_id'])
        if p >= 100: completed_spools.append(s['spool_id'])
    return {
        'project': project, 'date': today, 'stats': st, 'schedule': sched,
        'today_activity': today_act, 'steps_completed_today': steps_today,
        'completed_spools': completed_spools, 'total_spools': len(spools),
    }

# ── API: Projects ─────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def home():
    return render_template_string(HOME_HTML)

@app.route('/api/projects')
@login_required
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
@login_required
def project_page(project):
    return render_template_string(PROJECT_HTML, project=project)

@app.route('/api/project/<project>/dashboard')
@login_required
def api_project_dashboard(project):
    st = project_stats(project)
    act = db_fetchall("SELECT * FROM activity_log WHERE project=? ORDER BY timestamp DESC LIMIT 20", (project,))
    st['recent_activity'] = fix_timestamps(act)
    return jsonify(st)

@app.route('/api/project/<project>/spools')
@login_required
def api_project_spools(project):
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    result = []
    for s in spools:
        p = spool_progress(project, s['spool_id'])
        result.append({'spool': s, 'progress_pct': p})
    return jsonify(result)

# ── API: Spool Detail ─────────────────────────────────────────────────────────
@app.route('/project/<project>/spool/<spool_id>')
@login_required
def spool_page(project, spool_id):
    return render_template_string(SPOOL_HTML, project=project, spool_id=spool_id)

@app.route('/api/project/<project>/spool/<spool_id>')
@login_required
def api_spool(project, spool_id):
    sp = db_fetchone("SELECT * FROM spools WHERE project=? AND spool_id=?", (project, spool_id))
    if not sp: return jsonify({'error':'Not found'}), 404
    steps = fix_timestamps(db_fetchall("SELECT * FROM progress WHERE project=? AND spool_id=? ORDER BY step_number", (project, spool_id)))
    act = fix_timestamps(db_fetchall("SELECT * FROM activity_log WHERE project=? AND spool_id=? ORDER BY timestamp DESC LIMIT 10", (project, spool_id)))
    return jsonify({'spool':sp, 'progress_pct': spool_progress(project, spool_id), 'steps':steps, 'activity':act,
        'step_definitions':[{'number':s[0],'name_en':s[1],'name_cn':s[2],'weight':s[3]} for s in PRODUCTION_STEPS
            if s[0] != 16 or (sp.get('has_branches') if sp else False)],
        'has_branches': bool(sp.get('has_branches')) if sp else False})

@app.route('/api/project/<project>/spool/<spool_id>/step/<int:step>', methods=['POST'])
@login_required
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
                db_execute("INSERT INTO spools (project,spool_id,spool_full,iso_no,marking,mk_number,main_diameter,line,sequence,has_branches) VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT (project,spool_id) DO UPDATE SET has_branches=EXCLUDED.has_branches",
                    (proj, s['spool_id'], s.get('spool_full',''), s.get('iso_no',''), s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''), s.get('line',''), s.get('sequence',0), 1 if s.get('has_branches') else 0))
            else:
                db_execute("INSERT INTO spools (project,spool_id,spool_full,iso_no,marking,mk_number,main_diameter,line,sequence,has_branches) VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(project,spool_id) DO UPDATE SET has_branches=excluded.has_branches",
                    (proj, s['spool_id'], s.get('spool_full',''), s.get('iso_no',''), s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''), s.get('line',''), s.get('sequence',0), 1 if s.get('has_branches') else 0))
            has_br = 1 if s.get('has_branches') else 0
            for sn,_,_,_ in PRODUCTION_STEPS:
                if sn == 16 and not has_br:
                    continue
                if USE_PG:
                    db_execute("INSERT INTO progress (project,spool_id,step_number,completed) VALUES (?,?,?,0) ON CONFLICT (project,spool_id,step_number) DO NOTHING", (proj, s['spool_id'], sn))
                else:
                    db_execute("INSERT OR IGNORE INTO progress (project,spool_id,step_number,completed) VALUES (?,?,?,0)", (proj, s['spool_id'], sn))
            count += 1
        except Exception as e: print(f"Import error {s.get('spool_id','?')}: {e}")
    db_commit()
    return jsonify({'ok':True, 'imported':count})

@app.route('/api/project/<project>/export')
@login_required
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

@app.route('/api/project/<project>/spool/<spool_id>/weight', methods=['POST'])
@login_required
def api_update_weight(project, spool_id):
    d = request.get_json() or {}
    weight = d.get('weight_kg', 0)
    op = d.get('operator', '')
    db_execute("UPDATE spools SET actual_weight_kg=? WHERE project=? AND spool_id=?", (weight, project, spool_id))
    db_execute("INSERT INTO activity_log (project,spool_id,step_number,action,operator,details) VALUES (?,?,?,?,?,?)",
        (project, spool_id, 0, 'weight', op, f"Weight recorded: {weight} kg by {op}"))
    db_commit()
    return jsonify({'ok': True, 'weight_kg': weight})

@app.route('/api/project/<project>/spool/<spool_id>/drawing', methods=['POST'])
def api_upload_drawing(project, spool_id):
    """Upload a PDF drawing for a spool."""
    if 'file' in request.files:
        pdf_data = request.files['file'].read()
    else:
        pdf_data = request.get_data()
    if not pdf_data:
        return jsonify({'error': 'No data'}), 400
    if USE_PG:
        import psycopg2
        db_execute("DELETE FROM drawings WHERE project=%s AND spool_id=%s", (project, spool_id))
        cur = get_db().cursor()
        cur.execute("INSERT INTO drawings (project, spool_id, pdf_data) VALUES (%s, %s, %s)",
                    (project, spool_id, psycopg2.Binary(pdf_data)))
    else:
        db_execute("DELETE FROM drawings WHERE project=? AND spool_id=?", (project, spool_id))
        db_execute("INSERT INTO drawings (project, spool_id, pdf_data) VALUES (?,?,?)",
                    (project, spool_id, pdf_data))
    db_commit()
    return jsonify({'ok': True, 'size_kb': round(len(pdf_data)/1024, 1)})

@app.route('/api/project/<project>/spool/<spool_id>/drawing')
@login_required
def api_get_drawing(project, spool_id):
    """Serve the PDF drawing for a spool."""
    if USE_PG:
        cur = get_db().cursor()
        cur.execute("SELECT pdf_data FROM drawings WHERE project=%s AND spool_id=%s", (project, spool_id))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'No drawing'}), 404
        pdf_data = bytes(row[0])
    else:
        row = db_fetchone("SELECT pdf_data FROM drawings WHERE project=? AND spool_id=?", (project, spool_id))
        if not row:
            return jsonify({'error': 'No drawing'}), 404
        pdf_data = row['pdf_data']
    from flask import Response
    return Response(pdf_data, mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline; filename={spool_id}.pdf'})

@app.route('/api/project/<project>/drawings/list')
@login_required
def api_list_drawings(project):
    """List which spools have drawings uploaded."""
    if USE_PG:
        cur = get_db().cursor()
        cur.execute("SELECT spool_id, length(pdf_data) as size_bytes FROM drawings WHERE project=%s", (project,))
        rows = cur.fetchall()
        return jsonify([{'spool_id': r[0], 'size_kb': round(r[1]/1024,1)} for r in rows])
    else:
        rows = db_fetchall("SELECT spool_id, length(pdf_data) as size_bytes FROM drawings WHERE project=?", (project,))
        return jsonify([{'spool_id': r['spool_id'], 'size_kb': round(r['size_bytes']/1024,1)} for r in rows])

@app.route('/api/migrate', methods=['POST'])
def api_migrate():
    """Run DB migrations and clear data for fresh import."""
    results = []
    try:
        if USE_PG:
            try: db_execute("ALTER TABLE spools ADD COLUMN has_branches INTEGER DEFAULT 0"); results.append("added has_branches")
            except: get_db().rollback(); results.append("has_branches exists")
            try: db_execute("ALTER TABLE spools ADD COLUMN actual_weight_kg REAL DEFAULT 0"); results.append("added actual_weight_kg")
            except: get_db().rollback(); results.append("actual_weight_kg exists")
            try:
                cur = get_db().cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS drawings (id SERIAL PRIMARY KEY, project TEXT NOT NULL, spool_id TEXT NOT NULL, pdf_data BYTEA NOT NULL, UNIQUE(project, spool_id))")
                get_db().commit()
                results.append("created drawings table")
            except: get_db().rollback(); results.append("drawings table exists")
            try:
                cur = get_db().cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS schedule (id SERIAL PRIMARY KEY, project TEXT NOT NULL, diameter TEXT NOT NULL, task_type TEXT NOT NULL, description TEXT DEFAULT '', planned_start DATE NOT NULL, planned_end DATE NOT NULL, spool_count INTEGER DEFAULT 0, UNIQUE(project, diameter, task_type))")
                get_db().commit()
                results.append("created schedule table")
            except: get_db().rollback(); results.append("schedule table exists")
        else:
            try:
                db_execute("CREATE TABLE IF NOT EXISTS drawings (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, spool_id TEXT NOT NULL, pdf_data BLOB NOT NULL, UNIQUE(project, spool_id))")
                db_commit()
            except: pass
            try:
                db_execute("CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, diameter TEXT NOT NULL, task_type TEXT NOT NULL, description TEXT DEFAULT '', planned_start TEXT NOT NULL, planned_end TEXT NOT NULL, spool_count INTEGER DEFAULT 0, UNIQUE(project, diameter, task_type))")
                db_commit()
            except: pass
        # NOTE: Data clearing removed for safety. Use /api/project/<id>/spool/<id>/delete for individual cleanup.
        db_commit(); results.append("migration complete - no data cleared")
    except Exception as e: results.append(str(e))
    return jsonify({'ok': True, 'results': results})


@app.route('/api/project/<project>/spool/<spool_id>/delete', methods=['POST'])
def api_delete_spool(project, spool_id):
    db_execute("DELETE FROM activity_log WHERE project=? AND spool_id=?", (project, spool_id))
    db_execute("DELETE FROM progress WHERE project=? AND spool_id=?", (project, spool_id))
    db_execute("DELETE FROM spools WHERE project=? AND spool_id=?", (project, spool_id))
    db_commit()
    return jsonify({'ok': True, 'deleted': spool_id})

@app.route('/api/cleanup', methods=['POST'])
def api_cleanup():
    db_execute("DELETE FROM activity_log WHERE project=''")
    db_execute("DELETE FROM progress WHERE project=''")
    db_execute("DELETE FROM spools WHERE project=''")
    db_commit()
    return jsonify({'ok': True})

@app.route('/healthz')
def healthz():
    try: db_execute("SELECT 1"); return jsonify({'status':'ok','db':'connected'})
    except Exception as e: return jsonify({'status':'error','db':str(e)}), 500

# ── API: Schedule & Reports ──────────────────────────────────────────────────
@app.route('/api/project/<project>/schedule', methods=['POST'])
def api_set_schedule(project):
    """Import schedule data. Accepts either:
    1) JSON array of {diameter, task_type, planned_start, planned_end, spool_count, description}
    2) JSON with {fab_start: "YYYY-MM-DD"} to auto-calculate from spool data using Gantt logic.
    """
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON data'}), 400
    count = 0
    if isinstance(data, list):
        # Direct schedule import
        for item in data:
            if USE_PG:
                db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (project,diameter,task_type) DO UPDATE SET description=EXCLUDED.description,planned_start=EXCLUDED.planned_start,planned_end=EXCLUDED.planned_end,spool_count=EXCLUDED.spool_count",
                    (project, item['diameter'], item['task_type'], item.get('description',''), item['planned_start'], item['planned_end'], item.get('spool_count',0)))
            else:
                db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (?,?,?,?,?,?,?) ON CONFLICT(project,diameter,task_type) DO UPDATE SET description=excluded.description,planned_start=excluded.planned_start,planned_end=excluded.planned_end,spool_count=excluded.spool_count",
                    (project, item['diameter'], item['task_type'], item.get('description',''), item['planned_start'], item['planned_end'], item.get('spool_count',0)))
            count += 1
    elif isinstance(data, dict) and 'fab_start' in data:
        # Auto-calculate from spool data
        from datetime import timedelta
        fab_start = date.fromisoformat(data['fab_start'])
        spools = db_fetchall("SELECT main_diameter FROM spools WHERE project=?", (project,))
        diam_counts = {}
        for s in spools:
            d = (s['main_diameter'] or '?').replace('"','')
            if d not in diam_counts: diam_counts[d] = 0
            diam_counts[d] += 1
        current_fab = fab_start
        for diam in DIAMETER_ORDER:
            if diam not in diam_counts: continue
            cnt = diam_counts[diam]
            rate = SPOOLS_PER_DAY.get(diam, 2.0)
            fab_days = max(1, round(cnt / rate))
            fab_end = current_fab + timedelta(days=fab_days)
            paint_start = fab_end + timedelta(days=1)
            paint_end = paint_start + timedelta(days=PAINTING_DAYS)
            dk = f'{diam}"'
            for tt, sd, ed, desc in [
                ('fabrication', current_fab, fab_end, f'Fabrication {dk} ({cnt} spools)'),
                ('painting', paint_start, paint_end, f'Painting {dk}'),
            ]:
                if USE_PG:
                    db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (project,diameter,task_type) DO UPDATE SET description=EXCLUDED.description,planned_start=EXCLUDED.planned_start,planned_end=EXCLUDED.planned_end,spool_count=EXCLUDED.spool_count",
                        (project, dk, tt, desc, str(sd), str(ed), cnt))
                else:
                    db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (?,?,?,?,?,?,?) ON CONFLICT(project,diameter,task_type) DO UPDATE SET description=excluded.description,planned_start=excluded.planned_start,planned_end=excluded.planned_end,spool_count=excluded.spool_count",
                        (project, dk, tt, desc, str(sd), str(ed), cnt))
                count += 1
            overlap = max(1, round(fab_days * 0.4))
            current_fab = current_fab + timedelta(days=fab_days - overlap)
    db_commit()
    return jsonify({'ok': True, 'entries': count})

@app.route('/api/project/<project>/schedule')
@login_required
def api_get_schedule(project):
    rows = db_fetchall("SELECT * FROM schedule WHERE project=? ORDER BY planned_start", (project,))
    return jsonify(fix_timestamps(rows))

@app.route('/api/project/<project>/report')
@login_required
def api_report_data(project):
    return jsonify(generate_report_data(project))

@app.route('/project/<project>/report')
@login_required
def report_page(project):
    return render_template_string(REPORT_HTML, project=project)

@app.route('/api/project/<project>/report/download')
@login_required
def api_report_download(project):
    """Download a professional Excel production report for customer."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    import tempfile
    rpt = generate_report_data(project)
    st = rpt['stats']; sched = rpt.get('schedule')
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Production Report"
    hf = Font(bold=True, size=11, color='FFFFFF'); hfill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    bf = Font(size=10); bfb = Font(bold=True, size=10)
    green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    orange_fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
    red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
    thin = Border(left=Side('thin',color='C0C0C0'),right=Side('thin',color='C0C0C0'),top=Side('thin',color='C0C0C0'),bottom=Side('thin',color='C0C0C0'))
    # Title
    ws.merge_cells('A1:H1')
    ws['A1'] = f"ENERXON — Production Report / 生产报告"; ws['A1'].font = Font(bold=True, size=16, color='2F5496')
    ws['A2'] = f"Project: {project}"; ws['A2'].font = bfb
    ws['A3'] = f"Date: {rpt['date']}"; ws['A3'].font = bf
    ws['A4'] = f"Overall Progress: {st['overall_pct']}%"; ws['A4'].font = Font(bold=True, size=12, color='2F5496')
    ws['A5'] = f"Total: {st['total']} spools | Done: {st['completed']} | In Progress: {st['in_progress']} | Pending: {st['not_started']}"; ws['A5'].font = bf
    # Schedule status section
    row = 7
    if sched and sched.get('diameters'):
        status_label = {'on_time': 'ON TIME ✓', 'at_risk': 'AT RISK ⚠', 'delayed': 'DELAYED ✗', 'not_started': 'NOT STARTED'}
        ws.cell(row, 1, "PRODUCTION SCHEDULE STATUS / 生产计划状态").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        for col, h in enumerate(['Diameter','Spools','Expected %','Actual %','Diff','Status','Fab Start','Fab End','Paint End'], 1):
            c = ws.cell(row, col, h); c.font = hf; c.fill = hfill; c.alignment = Alignment(horizontal='center'); c.border = thin
        row += 1
        for d in sched['diameters']:
            ws.cell(row, 1, d['diameter']).font = bfb; ws.cell(row, 1).border = thin
            ws.cell(row, 2, d['spool_count']).font = bf; ws.cell(row, 2).alignment = Alignment(horizontal='center'); ws.cell(row, 2).border = thin
            ws.cell(row, 3, d['expected_pct']).font = bf; ws.cell(row, 3).alignment = Alignment(horizontal='center'); ws.cell(row, 3).border = thin
            ws.cell(row, 4, d['actual_pct']).font = bfb; ws.cell(row, 4).alignment = Alignment(horizontal='center'); ws.cell(row, 4).border = thin
            ws.cell(row, 5, d['diff']).font = bf; ws.cell(row, 5).alignment = Alignment(horizontal='center'); ws.cell(row, 5).border = thin
            sc = ws.cell(row, 6, status_label.get(d['status'], d['status']))
            sc.font = bfb; sc.alignment = Alignment(horizontal='center'); sc.border = thin
            if d['status'] == 'on_time': sc.fill = green_fill
            elif d['status'] == 'at_risk': sc.fill = orange_fill
            elif d['status'] == 'delayed': sc.fill = red_fill
            ws.cell(row, 7, d['fab_start']).font = bf; ws.cell(row, 7).border = thin
            ws.cell(row, 8, d['fab_end']).font = bf; ws.cell(row, 8).border = thin
            ws.cell(row, 9, d.get('paint_end','')).font = bf; ws.cell(row, 9).border = thin
            row += 1
        row += 1
        # Mini Gantt
        ws.cell(row, 1, "GANTT OVERVIEW / 甘特图概览").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        # Find date range for Gantt
        all_starts = [d['fab_start'] for d in sched['diameters'] if d['fab_start']]
        all_ends = [d.get('paint_end','') or d['fab_end'] for d in sched['diameters'] if d['fab_end']]
        if all_starts and all_ends:
            from datetime import timedelta
            gmin = date.fromisoformat(min(all_starts)); gmax = date.fromisoformat(max(all_ends))
            # Weeks
            week_start = gmin - timedelta(days=gmin.weekday())
            weeks = []
            cur = week_start
            while cur <= gmax + timedelta(days=7):
                weeks.append(cur); cur += timedelta(days=7)
            # Headers
            ws.cell(row, 1, 'Diameter').font = hf; ws.cell(row, 1).fill = hfill; ws.cell(row, 1).border = thin
            ws.cell(row, 2, 'Phase').font = hf; ws.cell(row, 2).fill = hfill; ws.cell(row, 2).border = thin
            for i, w in enumerate(weeks):
                c = ws.cell(row, 3+i, w.strftime('%d/%m'))
                c.font = Font(bold=True, size=7, color='FFFFFF'); c.fill = hfill; c.alignment = Alignment(horizontal='center'); c.border = thin
                ws.column_dimensions[openpyxl.utils.get_column_letter(3+i)].width = 4
            # Today marker column
            today_col = None
            for i, w in enumerate(weeks):
                wend = w + timedelta(days=6)
                if w <= date.today() <= wend: today_col = 3+i; break
            row += 1
            fab_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            paint_fill = PatternFill(start_color='70AD47', end_color='70AD47', fill_type='solid')
            today_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
            for d in sched['diameters']:
                for phase, ps, pe, fill in [('Fab', d['fab_start'], d['fab_end'], fab_fill), ('Paint', d.get('paint_start',''), d.get('paint_end',''), paint_fill)]:
                    if not ps or not pe: continue
                    ws.cell(row, 1, d['diameter']).font = bfb; ws.cell(row, 1).border = thin
                    ws.cell(row, 2, phase).font = bf; ws.cell(row, 2).border = thin
                    psd = date.fromisoformat(ps); ped = date.fromisoformat(pe)
                    for i, w in enumerate(weeks):
                        wend = w + timedelta(days=6)
                        col = 3+i
                        ws.cell(row, col).border = thin
                        if psd <= wend and ped >= w:
                            ws.cell(row, col).fill = fill
                        if today_col and col == today_col:
                            ws.cell(row, col).border = Border(left=Side('medium',color='FF0000'),right=Side('medium',color='FF0000'),top=Side('thin',color='C0C0C0'),bottom=Side('thin',color='C0C0C0'))
                    row += 1
    # Column widths
    ws.column_dimensions['A'].width = 14; ws.column_dimensions['B'].width = 10; ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12; ws.column_dimensions['E'].width = 8; ws.column_dimensions['F'].width = 16
    ws.column_dimensions['G'].width = 12; ws.column_dimensions['H'].width = 12; ws.column_dimensions['I'].width = 12
    # Today's activity
    row += 1
    if rpt.get('today_activity'):
        ws.cell(row, 1, f"TODAY'S ACTIVITY ({rpt['date']}) / 今日动态").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        for col, h in enumerate(['Time','Spool','Action','Operator','Details'], 1):
            c = ws.cell(row, col, h); c.font = hf; c.fill = hfill; c.border = thin
        row += 1
        for a in rpt['today_activity'][:50]:
            ts = str(a.get('timestamp',''))
            ws.cell(row, 1, ts[11:19] if len(ts)>11 else ts).font = bf; ws.cell(row, 1).border = thin
            ws.cell(row, 2, a.get('spool_id','')).font = bf; ws.cell(row, 2).border = thin
            ws.cell(row, 3, a.get('action','')).font = bf; ws.cell(row, 3).border = thin
            ws.cell(row, 4, a.get('operator','')).font = bf; ws.cell(row, 4).border = thin
            ws.cell(row, 5, a.get('details','')).font = bf; ws.cell(row, 5).border = thin
            row += 1
    ws.freeze_panes = 'A7'
    tmp = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False); wb.save(tmp.name)
    return send_file(tmp.name, as_attachment=True, download_name=f"{project}_report_{date.today().strftime('%Y%m%d')}.xlsx")

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
<div class="header"><div style="display:flex;align-items:center;gap:12px"><img src="data:image/png;base64,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" style="height:36px;filter:brightness(10)" alt="ENERXON"><div><h1 style="margin:0">Production Tracker</h1><div class="sub" style="margin:0">生产进度追踪系统 — Select a project / 选择项目</div></div></div></div>
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
  <div style="display:flex;align-items:center;gap:12px;margin-top:6px"><img src="data:image/png;base64,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" style="height:32px;filter:brightness(10)" alt="ENERXON"><div><h1 style="margin:0">{{ project }}</h1><div class="sub" style="margin:0">Production Progress / 生产进度</div></div></div>
</div>
<div class="stats-grid" id="stats"></div>
<div class="section"><h2>By Diameter / 按管径</h2><div class="diam-grid" id="diam"></div></div>
<div class="toolbar">
  <input type="text" id="q" placeholder="Search spool / 搜索管段..." oninput="filter()">
  <select id="fd" onchange="filter()"><option value="">All Diameters</option></select>
  <select id="fl" onchange="filter()"><option value="">All Lines</option><option value="A">Line A</option><option value="B">Line B</option><option value="C">Line C</option></select>
  <select id="fs" onchange="filter()"><option value="">All Status</option><option value="done">Done</option><option value="wip">In Progress</option><option value="todo">Not Started</option></select>
  <a class="btn" href="/api/project/{{ project }}/export">Export Excel</a>
  <a class="btn" href="/project/{{ project }}/report" style="background:#27ae60">📊 Report</a>
  <a class="btn" href="/api/project/{{ project }}/report/download" style="background:#ED7D31">📥 Report Excel</a>
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
  // Populate diameter dropdown
  const diamsSet = [...new Set(all.map(s=>s.spool.main_diameter||'?'))].sort((a,b)=>(parseInt(b)||0)-(parseInt(a)||0));
  const fdEl = document.getElementById('fd');
  const curFd = fdEl.value;
  fdEl.innerHTML = '<option value="">All Diameters</option>';
  diamsSet.forEach(d=>{ const o=document.createElement('option'); o.value=d; o.textContent=d; fdEl.appendChild(o); });
  fdEl.value = curFd;
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
  const q=document.getElementById('q').value.toLowerCase(),d=document.getElementById('fd').value,l=document.getElementById('fl').value,s=document.getElementById('fs').value;
  render(all.filter(x=>{
    if(q&&!x.spool.spool_id.toLowerCase().includes(q)&&!(x.spool.iso_no||'').toLowerCase().includes(q))return false;
    if(d&&(x.spool.main_diameter||'?')!==d)return false;
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
  <div style="display:flex;align-items:center;gap:12px;margin-top:6px"><img src="data:image/png;base64,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" style="height:28px;filter:brightness(10)" alt="ENERXON"><div><h1 style="margin:0">{{ spool_id }}</h1><div class="sub" style="margin:0" id="ss"></div></div></div>
</div>
<div class="info-bar" id="ib"></div>
<div class="prog"><div class="big" id="bp">0%</div><div class="lbl">Production Progress / 生产进度</div></div>
<div class="pbar-bg" style="margin:0 16px"><div class="pbar-fill" id="mb" style="width:0%"></div></div>
<div id="drawing-btn" style="padding:8px 16px;display:none">
  <a id="drawing-link" target="_blank" style="display:block;background:#2F5496;color:#fff;text-align:center;padding:12px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none">
    View Drawing / 查看图纸
  </a>
</div>
<div class="op-input"><input type="text" id="op" placeholder="Your name / 你的姓名"></div>
<div class="checklist" id="cl"></div>
<script>
const P='{{project}}',SID='{{spool_id}}'; let D;
async function load(){
  const r=await fetch(`/api/project/${P}/spool/${SID}`); D=await r.json(); render();
  // Check if drawing exists
  fetch(`/api/project/${P}/spool/${SID}/drawing`,{method:'HEAD'}).then(r=>{
    if(r.ok){
      document.getElementById('drawing-btn').style.display='block';
      document.getElementById('drawing-link').href=`/api/project/${P}/spool/${SID}/drawing`;
    }
  }).catch(()=>{});
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
    <div class="info-item"><span class="lb">MK:</span> <span class="vl">${s.mk_number||'-'}</span></div>
    <div class="info-item" style="flex-basis:100%;margin-top:4px"><span class="lb">Marking:</span> <span class="vl">${s.marking||'-'}</span></div>`;
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

  // Weight input at the end
  document.getElementById('cl').innerHTML += `
    <div style="background:#fff;border-radius:10px;padding:16px;margin-top:12px;box-shadow:0 1px 2px rgba(0,0,0,.05);border-left:4px solid #2F5496">
      <div style="font-size:13px;font-weight:600;color:#2F5496;margin-bottom:8px">Actual Weight / \u5b9e\u9645\u91cd\u91cf (kg)</div>
      <div style="display:flex;gap:8px;align-items:center">
        <input type="number" id="weight-input" placeholder="Enter weight in kg / \u8f93\u5165\u91cd\u91cf" value="${D.spool.actual_weight_kg||''}"
          style="flex:1;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:16px;font-weight:600" step="0.1" min="0">
        <button onclick="saveWeight()" style="background:#2F5496;color:#fff;border:none;padding:10px 20px;border-radius:6px;font-size:14px;cursor:pointer">Save</button>
      </div>
      ${D.spool.actual_weight_kg ? '<div style="font-size:11px;color:#888;margin-top:6px">\u2713 Weight recorded / \u91cd\u91cf\u5df2\u8bb0\u5f55</div>' : '<div style="font-size:11px;color:#e74c3c;margin-top:6px">\u26a0 Weight not recorded yet / \u91cd\u91cf\u5c1a\u672a\u8bb0\u5f55</div>'}
    </div>`;
}
async function saveWeight(){
  const w = document.getElementById('weight-input').value;
  const op = document.getElementById('op').value||'Unknown';
  await fetch('/api/project/'+P+'/spool/'+SID+'/weight',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({weight_kg:parseFloat(w)||0, operator:op})});
  await load();
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

# ── HTML: Production Report ──────────────────────────────────────────────────
REPORT_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ project }} — Production Report</title><style>""" + COMMON_CSS + """
.report-card{background:#fff;border-radius:12px;padding:20px;margin:12px 16px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.report-card h3{font-size:16px;color:#2F5496;margin-bottom:12px}
.status-badge{display:inline-block;padding:6px 16px;border-radius:20px;font-weight:700;font-size:14px;color:#fff}
.status-on_time{background:#27ae60}.status-at_risk{background:#f39c12}.status-delayed{background:#e74c3c}.status-not_started{background:#95a5a6}
.status-label{font-size:11px;text-transform:uppercase;letter-spacing:1px}
.diam-status{display:grid;gap:10px;margin-top:12px}
.diam-row{background:#f8f9fa;border-radius:8px;padding:14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.diam-row .d-name{font-size:18px;font-weight:700;color:#2F5496;min-width:50px}
.diam-row .d-info{flex:1;min-width:150px}
.diam-row .d-status{min-width:90px;text-align:center}
.gantt-mini{margin-top:12px;overflow-x:auto}
.gantt-table{border-collapse:collapse;width:100%;min-width:600px}
.gantt-table th{background:#2F5496;color:#fff;padding:4px;font-size:9px;text-align:center;position:sticky;top:0}
.gantt-table td{padding:3px 1px;border:1px solid #e8e8e8;height:20px;font-size:10px}
.gantt-table .g-label{white-space:nowrap;padding:3px 6px;font-weight:600;font-size:11px}
.g-fab{background:#4472C4}.g-paint{background:#70AD47}.g-today{border-left:2px solid #e74c3c;border-right:2px solid #e74c3c}
.act-item{padding:8px 12px;border-bottom:1px solid #f0f2f5;display:flex;gap:10px;align-items:center;font-size:13px}
.act-item .time{color:#888;font-size:11px;min-width:55px}.act-item .spool{font-weight:600;color:#2F5496;min-width:70px}
.act-item .detail{flex:1;color:#555}
.legend{display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;font-size:12px}
.legend span{display:flex;align-items:center;gap:4px}
.legend .box{width:14px;height:14px;border-radius:3px;display:inline-block}
.expected-bar{background:#e8e8e8;border-radius:6px;height:8px;position:relative;overflow:visible;margin-top:4px}
.expected-fill{position:absolute;left:0;top:0;height:100%;border-radius:6px;opacity:0.3;background:#2F5496}
.actual-fill{position:absolute;left:0;top:0;height:100%;border-radius:6px}
.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:12px 0}
.sum-card{text-align:center;padding:12px;border-radius:8px;background:#f8f9fa}
.sum-card .v{font-size:24px;font-weight:700}.sum-card .l{font-size:11px;color:#888;margin-top:2px}
@media print{.header{background:#2F5496!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}.no-print{display:none!important}}
</style></head><body>
<div class="header">
  <a class="back no-print" href="/project/{{ project }}">← Back / 返回</a>
  <h1>Production Report / 生产报告</h1>
  <div class="sub">{{ project }} — <span id="rpt-date"></span></div>
</div>
<div id="rpt-content"><div style="text-align:center;padding:40px;color:#888">Loading report... / 加载报告中...</div></div>
<div style="padding:16px;text-align:center" class="no-print">
  <a class="btn" href="/api/project/{{ project }}/report/download">📥 Download Excel Report / 下载Excel报告</a>
  <button class="btn" onclick="window.print()" style="margin-left:8px">🖨 Print / 打印</button>
</div>
<script>
const P='{{project}}';
const STATUS_LABELS = {on_time:'ON TIME / 按时',at_risk:'AT RISK / 有延迟风险',delayed:'DELAYED / 已延迟',not_started:'NOT STARTED / 未开始'};
const STATUS_COLORS = {on_time:'#27ae60',at_risk:'#f39c12',delayed:'#e74c3c',not_started:'#95a5a6'};
async function load(){
  const r = await fetch(`/api/project/${P}/report`);
  const d = await r.json();
  document.getElementById('rpt-date').textContent = d.date;
  let html = '';
  // Overall status
  const st = d.stats;
  const sch = d.schedule;
  const overallStatus = sch ? sch.overall_status : 'not_started';
  html += `<div class="report-card">
    <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
      <div><h3 style="margin:0">Overall Status / 总体状态</h3>
        <div class="status-badge status-${overallStatus}" style="margin-top:8px">${STATUS_LABELS[overallStatus]||overallStatus}</div></div>
      <div style="flex:1;min-width:200px">
        <div class="summary-grid">
          <div class="sum-card"><div class="v" style="color:#2F5496">${st.overall_pct}%</div><div class="l">Progress / 进度</div></div>
          <div class="sum-card"><div class="v">${st.total}</div><div class="l">Total / 总数</div></div>
          <div class="sum-card"><div class="v" style="color:#27ae60">${st.completed}</div><div class="l">Done / 完成</div></div>
          <div class="sum-card"><div class="v" style="color:#f39c12">${st.in_progress}</div><div class="l">WIP / 进行中</div></div>
          <div class="sum-card"><div class="v" style="color:#e74c3c">${st.not_started}</div><div class="l">Pending / 待开始</div></div>
        </div>
      </div>
    </div>
  </div>`;
  // Schedule status per diameter
  if(sch && sch.diameters && sch.diameters.length){
    html += `<div class="report-card"><h3>Schedule Status by Diameter / 按管径计划状态</h3><div class="diam-status">`;
    sch.diameters.forEach(dm => {
      const color = STATUS_COLORS[dm.status] || '#95a5a6';
      const barMax = Math.max(dm.expected_pct, dm.actual_pct, 1);
      html += `<div class="diam-row" style="border-left:4px solid ${color}">
        <div class="d-name">${dm.diameter}</div>
        <div class="d-info">
          <div style="font-size:12px;color:#888">${dm.spool_count} spools · Expected / 预期: ${dm.expected_pct}% · Actual / 实际: <strong>${dm.actual_pct}%</strong> (${dm.diff>=0?'+':''}${dm.diff}%)</div>
          <div class="expected-bar" style="margin-top:6px">
            <div class="expected-fill" style="width:${dm.expected_pct}%"></div>
            <div class="actual-fill" style="width:${dm.actual_pct}%;background:${color}"></div>
          </div>
          <div style="font-size:10px;color:#aaa;margin-top:2px">Fab: ${dm.fab_start} → ${dm.fab_end} · Paint → ${dm.paint_end || 'N/A'}</div>
        </div>
        <div class="d-status"><span class="status-badge status-${dm.status}" style="font-size:11px;padding:4px 10px">${STATUS_LABELS[dm.status]||dm.status}</span></div>
      </div>`;
    });
    html += `</div></div>`;
    // Mini Gantt
    html += `<div class="report-card"><h3>Gantt Overview / 甘特图概览</h3>
      <div class="legend">
        <span><span class="box" style="background:#4472C4"></span> Fabrication / 制作</span>
        <span><span class="box" style="background:#70AD47"></span> Painting / 涂装</span>
        <span><span class="box" style="background:#e74c3c;width:3px"></span> Today / 今天</span>
      </div>
      <div class="gantt-mini"><table class="gantt-table"><thead><tr><th style="min-width:70px">Diameter</th><th style="min-width:50px">Phase</th>`;
    // Calculate weeks
    const allStarts = sch.diameters.map(d=>d.fab_start).filter(x=>x);
    const allEnds = sch.diameters.map(d=>d.paint_end||d.fab_end).filter(x=>x);
    const gmin = new Date(Math.min(...allStarts.map(s=>new Date(s)))); const gmax = new Date(Math.max(...allEnds.map(s=>new Date(s))));
    gmin.setDate(gmin.getDate() - gmin.getDay() + 1); // Monday
    const weeks = []; let cur = new Date(gmin);
    while(cur <= new Date(gmax.getTime()+7*86400000)){weeks.push(new Date(cur)); cur.setDate(cur.getDate()+7);}
    const today = new Date(); today.setHours(0,0,0,0);
    weeks.forEach(w => { html += `<th>${w.toLocaleDateString('en',{day:'2-digit',month:'short'})}</th>`; });
    html += `</tr></thead><tbody>`;
    sch.diameters.forEach(dm => {
      [{phase:'Fab',start:dm.fab_start,end:dm.fab_end,cls:'g-fab'},{phase:'Paint',start:dm.paint_start,end:dm.paint_end,cls:'g-paint'}].forEach(ph => {
        if(!ph.start||!ph.end) return;
        const ps = new Date(ph.start), pe = new Date(ph.end);
        html += `<tr><td class="g-label">${dm.diameter}</td><td class="g-label">${ph.phase}</td>`;
        weeks.forEach(w => {
          const we = new Date(w.getTime()+6*86400000);
          let cls = '';
          if(ps<=we && pe>=w) cls = ph.cls;
          let todayCls = (today>=w && today<=we) ? ' g-today' : '';
          html += `<td class="${cls}${todayCls}"></td>`;
        });
        html += `</tr>`;
      });
    });
    html += `</tbody></table></div></div>`;
  } else {
    html += `<div class="report-card"><h3>Schedule Status / 计划状态</h3>
      <p style="color:#888;padding:20px 0">No schedule configured. Use the API to set up a production schedule:<br>
      <code>POST /api/project/${P}/schedule</code> with <code>{"fab_start":"YYYY-MM-DD"}</code></p></div>`;
  }
  // Today's activity
  html += `<div class="report-card"><h3>Today's Activity / 今日动态 (${d.steps_completed_today} steps completed)</h3>`;
  if(d.today_activity && d.today_activity.length){
    d.today_activity.forEach(a => {
      const ts = (a.timestamp||'').substring(11,19);
      const icon = a.action==='completed' ? '✅' : a.action==='unchecked' ? '↩️' : '📝';
      html += `<div class="act-item"><span class="time">${ts}</span><span class="spool">${a.spool_id}</span><span>${icon}</span><span class="detail">${a.details||a.action}</span></div>`;
    });
  } else {
    html += `<div style="text-align:center;padding:20px;color:#aaa">No activity today yet / 今天暂无动态</div>`;
  }
  html += `</div>`;
  document.getElementById('rpt-content').innerHTML = html;
}
load();
</script></body></html>"""

# ── Init & Run ────────────────────────────────────────────────────────────────
try: init_db(); print("DB initialized")
except Exception as e: print(f"DB init: {e}")

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST','0.0.0.0'), port=int(os.environ.get('PORT',5000)))
