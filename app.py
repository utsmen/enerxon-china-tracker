#!/usr/bin/env python3
"""
Charlie Tracker — Multi-Project Spool Production Tracking (Generalised)
URL structure: / → /project/<id> → /project/<id>/spool/<spool_id>
All ITP steps, diameters, and production rates are project-specific (no hardcoded constants).
"""
import os, sys, json
from datetime import datetime, date, timedelta
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
            app.permanent_session_lifetime = timedelta(days=90)
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

# Default step definitions — fallback when project has no steps defined yet
_DEFAULT_STEPS = [
    {'step_number':1,'name_en':'Material Receiving & Traceability','name_cn':'\u6765\u6599\u68c0\u9a8c\u53ca\u53ef\u8ffd\u6eaf\u6027','weight':5,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':1,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':2,'name_en':'Documentation Review (WPS/PQR/ITP)','name_cn':'\u6587\u4ef6\u5ba1\u67e5\uff08WPS/PQR/ITP\uff09','weight':3,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':2,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':3,'name_en':'Pipe Cutting \u2014 Dimensional Check','name_cn':'\u7ba1\u9053\u5207\u5272 \u2014 \u5c3a\u5bf8\u68c0\u9a8c','weight':8,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':3,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':4,'name_en':'End Preparation / Bevelling','name_cn':'\u7ba1\u53e3\u51c6\u5907 / \u5761\u53e3\u52a0\u5de5','weight':5,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':4,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':5,'name_en':'Fit-Up & Assembly Inspection','name_cn':'\u7ec4\u5bf9\u53ca\u88c5\u914d\u68c0\u9a8c','weight':10,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':5,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':16,'name_en':'Branch Welding','name_cn':'\u652f\u7ba1\u710a\u63a5','weight':5,'category':'branch','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':6,'is_conditional':1,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':6,'name_en':'Production Welding as per WPS','name_cn':'\u6309WPS\u4e3b\u7ba1\u710a\u63a5','weight':10,'category':'welding','hours_fixed':0,'hours_variable':'welding','spool_type':'ALL','display_order':7,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':7,'name_en':'Visual Inspection (VT) \u2014 100%','name_cn':'\u76ee\u89c6\u68c0\u9a8cVT\uff08\u5168\u68c0\uff09','weight':8,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':8,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':8,'name_en':'Radiographic Test (RT) \u2014 100%','name_cn':'\u5c04\u7ebf\u68c0\u6d4bRT\uff08\u5168\u68c0\uff09\u2605\u505c\u6b62\u70b9','weight':10,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':9,'is_conditional':0,'is_hold_point':1,'is_release':0,'phase':'fab'},
    {'step_number':9,'name_en':'Magnetic Particle (MT) \u2014 100%','name_cn':'\u78c1\u7c89\u68c0\u6d4bMT\uff08\u5168\u68c0\uff09','weight':5,'category':'fab_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':10,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'fab'},
    {'step_number':10,'name_en':'Cleaning Prior to Painting','name_cn':'\u6d82\u88c5\u524d\u6e05\u6d01\u5904\u7406','weight':3,'category':'paint_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':11,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'paint'},
    {'step_number':11,'name_en':'Surface Preparation \u2014 Blasting','name_cn':'\u8868\u9762\u5904\u7406 \u2014 \u55b7\u7802','weight':8,'category':'surface_treatment','hours_fixed':0,'hours_variable':'surface','spool_type':'ALL','display_order':12,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'paint'},
    {'step_number':12,'name_en':'Painting Application','name_cn':'\u6d82\u88c5\u65bd\u5de5\uff08\u5e95\u6f06/\u4e2d\u95f4\u6f06/\u9762\u6f06\uff09','weight':8,'category':'surface_treatment','hours_fixed':0,'hours_variable':'surface','spool_type':'ALL','display_order':13,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'paint'},
    {'step_number':13,'name_en':'Coating Inspection \u2014 DFT','name_cn':'\u6d82\u5c42\u68c0\u9a8c \u2014 \u819c\u539a\u53ca\u9644\u7740\u529b','weight':4,'category':'paint_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':14,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'paint'},
    {'step_number':14,'name_en':'Dimensional Inspection & Marking','name_cn':'\u5c3a\u5bf8\u68c0\u9a8c\u53ca\u6807\u8bc6','weight':5,'category':'paint_fixed','hours_fixed':2.0,'hours_variable':'','spool_type':'ALL','display_order':15,'is_conditional':0,'is_hold_point':0,'is_release':0,'phase':'paint'},
    {'step_number':15,'name_en':'Final Inspection \u2014 Released','name_cn':'\u6700\u7ec8\u68c0\u9a8c \u2014 \u53d1\u8d27\u653e\u884c \u2605\u89c1\u8bc1','weight':3,'category':'packing','hours_fixed':3.0,'hours_variable':'','spool_type':'ALL','display_order':16,'is_conditional':0,'is_hold_point':0,'is_release':1,'phase':'paint'},
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
        # Execute each statement separately so one failure doesn't block the rest
        pg_statements = [
            "CREATE TABLE IF NOT EXISTS spools (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, spool_full TEXT DEFAULT '', iso_no TEXT DEFAULT '', marking TEXT DEFAULT '', mk_number TEXT DEFAULT '', main_diameter TEXT DEFAULT '', line TEXT DEFAULT '', sequence INTEGER DEFAULT 0, project TEXT DEFAULT '', has_branches INTEGER DEFAULT 0, spool_type TEXT DEFAULT 'SPOOL', actual_weight_kg REAL DEFAULT 0, surface_m2 REAL DEFAULT 0, joint_count INTEGER DEFAULT 0, raf_inches REAL DEFAULT 0, created_at TIMESTAMP DEFAULT NOW(), UNIQUE(project, spool_id))",
            "CREATE TABLE IF NOT EXISTS progress (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER NOT NULL, completed INTEGER DEFAULT 0, completed_by TEXT DEFAULT '', completed_at TIMESTAMP, remarks TEXT DEFAULT '', UNIQUE(project, spool_id, step_number))",
            "CREATE TABLE IF NOT EXISTS activity_log (id SERIAL PRIMARY KEY, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER, action TEXT NOT NULL, operator TEXT DEFAULT '', timestamp TIMESTAMP DEFAULT NOW(), details TEXT DEFAULT '')",
            "CREATE INDEX IF NOT EXISTS idx_progress_ps ON progress(project, spool_id)",
            "CREATE INDEX IF NOT EXISTS idx_activity_ps ON activity_log(project, spool_id)",
            "CREATE TABLE IF NOT EXISTS schedule (id SERIAL PRIMARY KEY, project TEXT NOT NULL, diameter TEXT NOT NULL, task_type TEXT NOT NULL, description TEXT DEFAULT '', planned_start DATE NOT NULL, planned_end DATE NOT NULL, spool_count INTEGER DEFAULT 0, UNIQUE(project, diameter, task_type))",
            "CREATE TABLE IF NOT EXISTS project_settings (id SERIAL PRIMARY KEY, project TEXT NOT NULL, key TEXT NOT NULL, value TEXT DEFAULT '', UNIQUE(project, key))",
            "CREATE TABLE IF NOT EXISTS drawings (id SERIAL PRIMARY KEY, project TEXT NOT NULL, spool_id TEXT NOT NULL, pdf_data BYTEA NOT NULL, UNIQUE(project, spool_id))",
            "CREATE TABLE IF NOT EXISTS project_steps (id SERIAL PRIMARY KEY, project TEXT NOT NULL, step_number INTEGER NOT NULL, name_en TEXT NOT NULL, name_cn TEXT NOT NULL DEFAULT '', weight INTEGER DEFAULT 5, category TEXT NOT NULL, hours_fixed REAL DEFAULT 2.0, hours_variable TEXT DEFAULT '', spool_type TEXT DEFAULT 'ALL', display_order INTEGER NOT NULL, is_conditional INTEGER DEFAULT 0, is_hold_point INTEGER DEFAULT 0, is_release INTEGER DEFAULT 0, phase TEXT DEFAULT 'fab', UNIQUE(project, step_number))",
            # Ensure spool_type column exists on old spools tables and backfill NULLs
            "ALTER TABLE spools ADD COLUMN spool_type TEXT DEFAULT 'SPOOL'",
            "UPDATE spools SET spool_type = 'SPOOL' WHERE spool_type IS NULL",
            # Migrate legacy schedule task_type names to phase names
            "UPDATE schedule SET task_type = 'fab' WHERE task_type IN ('fabrication', 'Fabricacion')",
            "UPDATE schedule SET task_type = 'paint' WHERE task_type IN ('painting', 'Pintura')",
        ]
        for stmt in pg_statements:
            try: cur.execute(stmt)
            except Exception as e: print(f"init_db skip: {e}")
        c.close()
    else:
        import sqlite3
        c = sqlite3.connect(os.environ.get('SQLITE_PATH','tracker.db'))
        c.executescript("""
            CREATE TABLE IF NOT EXISTS spools (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, spool_full TEXT DEFAULT '', iso_no TEXT DEFAULT '', marking TEXT DEFAULT '', mk_number TEXT DEFAULT '', main_diameter TEXT DEFAULT '', line TEXT DEFAULT '', sequence INTEGER DEFAULT 0, project TEXT DEFAULT '', has_branches INTEGER DEFAULT 0, spool_type TEXT DEFAULT 'SPOOL', actual_weight_kg REAL DEFAULT 0, surface_m2 REAL DEFAULT 0, joint_count INTEGER DEFAULT 0, raf_inches REAL DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), UNIQUE(project, spool_id));
            CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER NOT NULL, completed INTEGER DEFAULT 0, completed_by TEXT DEFAULT '', completed_at TEXT, remarks TEXT DEFAULT '', UNIQUE(project, spool_id, step_number));
            CREATE TABLE IF NOT EXISTS activity_log (id INTEGER PRIMARY KEY AUTOINCREMENT, spool_id TEXT NOT NULL, project TEXT DEFAULT '', step_number INTEGER, action TEXT NOT NULL, operator TEXT DEFAULT '', timestamp TEXT DEFAULT (datetime('now')), details TEXT DEFAULT '');
            CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, diameter TEXT NOT NULL, task_type TEXT NOT NULL, description TEXT DEFAULT '', planned_start TEXT NOT NULL, planned_end TEXT NOT NULL, spool_count INTEGER DEFAULT 0, UNIQUE(project, diameter, task_type));
            CREATE TABLE IF NOT EXISTS project_settings (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, key TEXT NOT NULL, value TEXT DEFAULT '', UNIQUE(project, key));
            CREATE TABLE IF NOT EXISTS drawings (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, spool_id TEXT NOT NULL, pdf_data BLOB NOT NULL, UNIQUE(project, spool_id));
            CREATE TABLE IF NOT EXISTS project_steps (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, step_number INTEGER NOT NULL, name_en TEXT NOT NULL, name_cn TEXT NOT NULL DEFAULT '', weight INTEGER DEFAULT 5, category TEXT NOT NULL, hours_fixed REAL DEFAULT 2.0, hours_variable TEXT DEFAULT '', spool_type TEXT DEFAULT 'ALL', display_order INTEGER NOT NULL, is_conditional INTEGER DEFAULT 0, is_hold_point INTEGER DEFAULT 0, is_release INTEGER DEFAULT 0, phase TEXT DEFAULT 'fab', UNIQUE(project, step_number));
            UPDATE schedule SET task_type = 'fab' WHERE task_type IN ('fabrication', 'Fabricacion');
            UPDATE schedule SET task_type = 'paint' WHERE task_type IN ('painting', 'Pintura');
        """); c.close()

# ── Helpers: Project Steps & Settings ─────────────────────────────────────────
def get_project_steps(project):
    """Load step definitions for a project from DB. Cached per request."""
    cache_key = f'_steps_{project}'
    if hasattr(g, cache_key):
        return getattr(g, cache_key)
    rows = db_fetchall("SELECT * FROM project_steps WHERE project=? ORDER BY display_order", (project,))
    if not rows:
        # Fallback: seed legacy 424 steps for this project
        rows = _DEFAULT_STEPS
    setattr(g, cache_key, rows)
    return rows

def get_project_settings(project):
    """Get project settings with defaults."""
    rows = db_fetchall("SELECT key, value FROM project_settings WHERE project=?", (project,))
    settings = {r['key']: r['value'] for r in rows}
    # Migrate old setting names to new ones
    key_migrations = {'painting_capability_m2d': 'surface_capability_m2d', 'painting_days': 'secondary_phase_days'}
    for old_key, new_key in key_migrations.items():
        if old_key in settings and new_key not in settings:
            settings[new_key] = settings[old_key]
    defaults = {'committed_weeks_saved':'0', 'committed_days_saved':'0', 'sea_transit_days':'45',
                'standard_weeks':'9', 'welding_capability_ipd':'1000', 'surface_capability_m2d':'91',
                'spools_per_day':'{}', 'secondary_phase_days':'13'}
    for k,v in defaults.items():
        if k not in settings: settings[k] = v
    return settings

def get_diameter_order(project):
    """Get diameter order for a project, sorted descending by numeric value."""
    rows = db_fetchall("SELECT DISTINCT main_diameter FROM spools WHERE project=? AND main_diameter != '' AND main_diameter != ?", (project, '?'))
    diameters = []
    for r in rows:
        d = (r['main_diameter'] or '').replace('"', '')
        try: diameters.append((float(d), d))
        except ValueError: diameters.append((0, d))
    diameters.sort(reverse=True)
    return [d[1] for d in diameters]

# ── Helpers: Progress Calculation ─────────────────────────────────────────────
def get_phase_order(steps_def):
    """Get ordered list of distinct phases from step definitions (by first appearance in display_order)."""
    seen = set(); phases = []
    for s in steps_def:
        p = s['phase']
        if p not in seen: seen.add(p); phases.append(p)
    return phases

def spool_hours(spool_row, completed_steps, settings, steps_def):
    """Calculate hours-based progress for a single spool. Phases are dynamic — derived from step definitions."""
    raf = float(spool_row.get('raf_inches') or 0)
    surface = float(spool_row.get('surface_m2') or 0)
    has_br = spool_row.get('has_branches', 0)
    spool_type = spool_row.get('spool_type', 'SPOOL') or 'SPOOL'
    weld_cap = float(settings.get('welding_capability_ipd', '552'))
    surface_cap = float(settings.get('surface_capability_m2d', '91'))

    # Pre-count surface steps per phase for even splitting
    surface_count_by_phase = {}
    for step in steps_def:
        if step['hours_variable'] == 'surface' and step['phase']:
            surface_count_by_phase[step['phase']] = surface_count_by_phase.get(step['phase'], 0) + 1

    # Determine which phases need surface area (contain surface_treatment steps)
    phases_with_surface = set(surface_count_by_phase.keys())

    # Accumulate per phase
    phase_totals = {}  # {phase: {total, done}}
    weld_hrs = 0.0; surface_hrs = 0.0

    for step in steps_def:
        sn = step['step_number']
        phase = step['phase']
        if step['is_conditional'] and not has_br: continue
        st = step.get('spool_type', 'ALL') or 'ALL'
        if st != 'ALL' and st != spool_type: continue

        # Calculate hours for this step
        if step['hours_variable'] == 'welding':
            hrs = (raf / weld_cap * 8) if weld_cap > 0 and raf > 0 else 0
            weld_hrs = hrs
        elif step['hours_variable'] == 'surface':
            if surface <= 0: continue
            n_surface = surface_count_by_phase.get(phase, 1)
            total_surface_hrs = (surface * 0.98 / surface_cap * 8) if surface_cap > 0 else 0
            hrs = total_surface_hrs / n_surface if n_surface > 0 else 0
            surface_hrs += hrs
        else:
            # Fixed hours — skip if this phase requires surface and spool has none
            if phase in phases_with_surface and surface <= 0: continue
            hrs = float(step.get('hours_fixed', 2.0) or 2.0)

        if phase not in phase_totals: phase_totals[phase] = {'total': 0.0, 'done': 0.0}
        phase_totals[phase]['total'] += hrs
        if sn in completed_steps: phase_totals[phase]['done'] += hrs

    # Calculate percentages per phase
    phases = {}
    total = 0.0; done = 0.0
    for phase, pt in phase_totals.items():
        pct = round(pt['done'] / pt['total'] * 100, 1) if pt['total'] > 0 else 0.0
        phases[phase] = {'total': pt['total'], 'done': pt['done'], 'pct': pct}
        total += pt['total']; done += pt['done']

    pct = round(done / total * 100, 1) if total > 0 else 0.0

    return {
        'phases': phases, 'total': total, 'done': done, 'pct': pct,
        'raf_inches': raf, 'surface_m2': surface, 'weld_hrs': weld_hrs, 'surface_hrs': surface_hrs,
    }

def bulk_spool_progress(project, settings=None):
    """Calculate hours-based progress for ALL spools at once."""
    if not settings: settings = get_project_settings(project)
    steps_def = get_project_steps(project)
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    all_progress = db_fetchall("SELECT spool_id, step_number, completed FROM progress WHERE project=?", (project,))
    completed_map = {}
    for r in all_progress:
        if r['completed']:
            if r['spool_id'] not in completed_map: completed_map[r['spool_id']] = set()
            completed_map[r['spool_id']].add(r['step_number'])
    result = {}
    for s in spools:
        sid = s['spool_id']
        done_steps = completed_map.get(sid, set())
        result[sid] = spool_hours(s, done_steps, settings, steps_def)
        result[sid]['spool'] = s
        result[sid]['done_steps'] = done_steps
    return result

def spool_progress(project, spool_id):
    """Hours-based progress for a single spool. Returns percentage."""
    settings = get_project_settings(project)
    steps_def = get_project_steps(project)
    sp = db_fetchone("SELECT * FROM spools WHERE project=? AND spool_id=?", (project, spool_id))
    if not sp: return 0.0
    rows = db_fetchall("SELECT step_number, completed FROM progress WHERE project=? AND spool_id=?", (project, spool_id))
    done_steps = set(r['step_number'] for r in rows if r['completed'])
    return spool_hours(sp, done_steps, settings, steps_def)['pct']

def project_stats(project):
    settings = get_project_settings(project)
    steps_def = get_project_steps(project)
    phase_order = get_phase_order(steps_def)
    bulk = bulk_spool_progress(project, settings)
    spools = [v for v in bulk.values()]
    total = len(spools)
    st = {'total':total,'completed':0,'in_progress':0,'not_started':0,'overall_pct':0.0,'by_diameter':{},'by_line':{},'phase_order':phase_order}
    tp = 0
    for v in spools:
        p = v['pct']; tp += p; s = v['spool']
        if p>=100: st['completed']+=1
        elif p>0: st['in_progress']+=1
        else: st['not_started']+=1
        d = s['main_diameter'] or '?'
        if d not in st['by_diameter']:
            st['by_diameter'][d] = {'total':0,'pct_sum':0,'phase_pct_sums':{ph:0 for ph in phase_order}}
        st['by_diameter'][d]['total']+=1; st['by_diameter'][d]['pct_sum']+=p
        for ph in phase_order:
            st['by_diameter'][d]['phase_pct_sums'][ph] += v['phases'].get(ph, {}).get('pct', 0)
        l = s['line'] or '?'
        if l not in st['by_line']: st['by_line'][l] = {'total':0,'pct_sum':0}
        st['by_line'][l]['total']+=1; st['by_line'][l]['pct_sum']+=p
    if total: st['overall_pct'] = round(tp/total,1)
    for v in st['by_diameter'].values():
        v['avg_pct'] = round(v['pct_sum']/v['total'],1) if v['total'] else 0
        v['phase_avgs'] = {}
        for ph in phase_order:
            v['phase_avgs'][ph] = round(v['phase_pct_sums'][ph]/v['total'],1) if v['total'] else 0
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

def schedule_status(project, bulk=None):
    """Calculate on-track/danger/delay status per diameter."""
    sched = db_fetchall("SELECT * FROM schedule WHERE project=? ORDER BY planned_start", (project,))
    if not sched: return None
    if not bulk: bulk = bulk_spool_progress(project)
    steps_def = get_project_steps(project)
    phase_order = get_phase_order(steps_def)
    settings = get_project_settings(project)
    diam_order = get_diameter_order(project)
    std_weeks = int(settings.get('standard_weeks', '9'))
    wks_saved = int(settings.get('committed_weeks_saved', '0'))
    days_saved = int(settings.get('committed_days_saved', '0'))
    total_saved = wks_saved * 7 + days_saved
    has_expediting = total_saved > 0
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    today = date.today()
    # Find production start
    prod_start = None
    for sc in sched:
        sd = parse_date(sc['planned_start'])
        if sd and (prod_start is None or sd < prod_start): prod_start = sd
    if prod_start and has_expediting:
        std_end = prod_start + timedelta(days=std_weeks * 7 - 1)
        committed_end = std_end - timedelta(days=total_saved)
    else:
        committed_end = None
    # Group spools by diameter
    by_diam = {}
    for s in spools:
        d = s['main_diameter'] or '?'
        if d not in by_diam: by_diam[d] = []
        by_diam[d].append(s)
    # Build schedule map
    sched_map = {}
    for sc in sched:
        d = sc['diameter']
        if d not in sched_map: sched_map[d] = {}
        sd = parse_date(sc['planned_start']); ed = parse_date(sc['planned_end'])
        sched_map[d][sc['task_type']] = {'start': str(sd) if sd else '', 'end': str(ed) if ed else '', 'spool_count': sc.get('spool_count',0), 'description': sc.get('description','')}
    fc = forecast_production(project, bulk)
    fc_diams = fc['diameters'] if fc else {}
    result = []
    overall_expected = 0; overall_actual = 0; overall_count = 0
    for diam in diam_order:
        dk = f'{diam}"'
        if dk not in sched_map and diam not in sched_map: continue
        sm = sched_map.get(dk, sched_map.get(diam, {}))
        # Build phase_dates from schedule map using phase names
        phase_dates = {}
        for ph in phase_order:
            ph_entry = sm.get(ph, {})
            if ph_entry:
                ps = parse_date(ph_entry.get('start')); pe = parse_date(ph_entry.get('end'))
                if ps and pe:
                    phase_dates[ph] = {'start': str(ps), 'end': str(pe)}
        if not phase_dates: continue
        first_phase = phase_order[0] if phase_order else None
        if not first_phase or first_phase not in phase_dates: continue
        try:
            total_start_d = min(parse_date(pd['start']) for pd in phase_dates.values())
            total_end_d = max(parse_date(pd['end']) for pd in phase_dates.values())
            target_end = committed_end if committed_end else total_end_d
            total_days = max(1, (target_end - total_start_d).days)
            elapsed = max(0, min((today - total_start_d).days, total_days))
            expected_pct = round(elapsed / total_days * 100, 1) if total_days > 0 else 0
        except: continue
        diam_spools = by_diam.get(dk, by_diam.get(f'{diam}"', []))
        if not diam_spools: continue
        actual_sum = sum(bulk.get(s['spool_id'], {}).get('pct', 0) for s in diam_spools)
        actual_pct = round(actual_sum / len(diam_spools), 1)
        # Per-phase averages (dynamic)
        phase_avgs = {}
        for ph in phase_order:
            ph_sum = sum(bulk.get(s['spool_id'], {}).get('phases', {}).get(ph, {}).get('pct', 0) for s in diam_spools)
            phase_avgs[ph] = round(ph_sum / len(diam_spools), 1)
        diff = actual_pct - expected_pct
        diam_fc = fc_diams.get(dk, {})
        fc_end = parse_date(diam_fc.get('forecast_end')) if diam_fc.get('forecast_end') else None
        if not diam_fc.get('started') and actual_pct == 0:
            status = 'not_started'
        elif fc_end and target_end:
            days_diff = (target_end - fc_end).days
            diff = days_diff
            if days_diff >= 0: status = 'on_time'
            elif days_diff >= -7: status = 'at_risk'
            else: status = 'delayed'
        else:
            if diff >= -5: status = 'on_time'
            elif diff >= -15: status = 'at_risk'
            else: status = 'delayed'
        overall_expected += expected_pct; overall_actual += actual_pct; overall_count += 1
        # First phase = fabrication for remaining RAF, last phase for remaining surface
        first_phase = phase_order[0] if phase_order else 'fab'
        remaining_raf = sum(bulk.get(s['spool_id'], {}).get('raf_inches', 0) for s in diam_spools if bulk.get(s['spool_id'], {}).get('phases', {}).get(first_phase, {}).get('pct', 0) < 100)
        remaining_m2 = sum(float(s.get('surface_m2') or 0) * 0.98 for s in diam_spools if bulk.get(s['spool_id'], {}).get('pct', 0) < 100)
        result.append({
            'diameter': dk, 'spool_count': len(diam_spools),
            'expected_pct': expected_pct, 'actual_pct': actual_pct, 'diff': round(diff, 1), 'status': status,
            'phase_avgs': phase_avgs,
            'remaining_raf': round(remaining_raf, 0), 'remaining_m2': round(remaining_m2, 1),
            'phase_dates': phase_dates,
            'total_start': str(total_start_d), 'total_end': str(total_end_d),
        })
    statuses = [r['status'] for r in result if r['status'] != 'not_started']
    if 'delayed' in statuses: overall_status = 'delayed'
    elif 'at_risk' in statuses: overall_status = 'at_risk'
    elif statuses: overall_status = 'on_time'
    else: overall_status = 'not_started'
    return {'diameters': result, 'overall_status': overall_status, 'today': str(today), 'phase_order': phase_order}

def daily_activity(project, day=None):
    if not day: day = date.today().strftime('%Y-%m-%d')
    if USE_PG:
        rows = db_fetchall("SELECT * FROM activity_log WHERE project=? AND timestamp::date = ?::date ORDER BY timestamp DESC", (project, day))
    else:
        rows = db_fetchall("SELECT * FROM activity_log WHERE project=? AND timestamp LIKE ? ORDER BY timestamp DESC", (project, f"{day}%"))
    return fix_timestamps(rows)

def forecast_production(project, bulk=None):
    """Forecast per diameter using actual throughput rates."""
    sched = db_fetchall("SELECT * FROM schedule WHERE project=? ORDER BY planned_start", (project,))
    if not sched: return None
    settings = get_project_settings(project)
    steps_def = get_project_steps(project)
    phase_order = get_phase_order(steps_def)
    diam_order = get_diameter_order(project)
    weld_cap = float(settings.get('welding_capability_ipd', '1000'))
    paint_cap = float(settings.get('surface_capability_m2d', '91'))
    if not bulk: bulk = bulk_spool_progress(project, settings)
    today = date.today()

    # Find welding and surface step numbers dynamically
    welding_steps = {s['step_number'] for s in steps_def if s['hours_variable'] == 'welding'}
    surface_steps = [s['step_number'] for s in steps_def if s['hours_variable'] == 'surface']
    last_surface_step = surface_steps[-1] if surface_steps else None

    prod_start = None
    for sc in sched:
        sd = parse_date(sc['planned_start'])
        if sd and (prod_start is None or sd < prod_start): prod_start = sd
    if not prod_start: prod_start = today
    global_days_elapsed = max(1, (today - prod_start).days)
    std_weeks = int(settings.get('standard_weeks', '9'))
    wks_saved = int(settings.get('committed_weeks_saved', '0'))
    days_saved = int(settings.get('committed_days_saved', '0'))
    total_saved = wks_saved * 7 + days_saved
    std_end = prod_start + timedelta(days=std_weeks * 7 - 1)
    committed_end = std_end - timedelta(days=total_saved) if total_saved > 0 else std_end

    # Per-diameter elapsed days
    if USE_PG:
        earliest_rows = db_fetchall(
            "SELECT s.main_diameter, MIN(p.completed_at) as first_activity "
            "FROM progress p JOIN spools s ON p.spool_id=s.spool_id AND p.project=s.project "
            "WHERE p.project=%s AND p.completed=1 GROUP BY s.main_diameter", (project,))
    else:
        earliest_rows = db_fetchall(
            "SELECT s.main_diameter, MIN(p.completed_at) as first_activity "
            "FROM progress p JOIN spools s ON p.spool_id=s.spool_id AND p.project=s.project "
            "WHERE p.project=? AND p.completed=1 GROUP BY s.main_diameter", (project,))
    diam_first_activity = {}
    for r in earliest_rows:
        d = r['main_diameter']; fa = parse_date(r['first_activity'])
        if d and fa: diam_first_activity[d] = fa

    by_diam = {}
    for sid, info in bulk.items():
        s = info['spool']; d = s['main_diameter'] or '?'
        if d not in by_diam: by_diam[d] = []
        by_diam[d].append(info)

    # Actual rates
    welded_raf_total = sum(i['raf_inches'] for i in bulk.values() if welding_steps & i.get('done_steps', set()))
    actual_weld_ipd = round(welded_raf_total / global_days_elapsed, 1) if global_days_elapsed > 0 else 0
    painted_m2_total = sum(i['surface_m2'] * 0.98 for i in bulk.values() if last_surface_step and last_surface_step in i.get('done_steps', set()))
    actual_paint_m2d = round(painted_m2_total / global_days_elapsed, 1) if global_days_elapsed > 0 else 0

    started_rates = []
    for diam in diam_order:
        dk = f'{diam}"'
        diam_infos = by_diam.get(dk, [])
        if not diam_infos: continue
        done_hrs = sum(i['done'] for i in diam_infos)
        if done_hrs > 0:
            first_activity = diam_first_activity.get(dk, prod_start)
            diam_elapsed = max(1, (today - first_activity).days)
            started_rates.append(done_hrs / diam_elapsed)
    avg_rate = sum(started_rates) / len(started_rates) if started_rates else None

    fc_result = {}
    overall_forecast = None
    for diam in diam_order:
        dk = f'{diam}"'
        diam_infos = by_diam.get(dk, [])
        if not diam_infos: continue
        total_hrs = sum(i['total'] for i in diam_infos)
        done_hrs = sum(i['done'] for i in diam_infos)
        remaining_hrs = total_hrs - done_hrs
        # Per-phase averages (dynamic)
        phase_avgs = {}
        for ph in phase_order:
            ph_sum = sum(i['phases'].get(ph, {}).get('pct', 0) for i in diam_infos)
            phase_avgs[ph] = round(ph_sum / len(diam_infos), 1)
        overall_pct = done_hrs / total_hrs * 100 if total_hrs > 0 else 0
        started = done_hrs > 0
        first_phase = phase_order[0] if phase_order else 'fab'
        remaining_raf = sum(i['raf_inches'] for i in diam_infos if i['phases'].get(first_phase, {}).get('pct', 0) < 100)
        remaining_m2 = sum(i['surface_m2'] * 0.98 for i in diam_infos if i['pct'] < 100)
        total_raf = sum(i['raf_inches'] for i in diam_infos)
        total_m2 = sum(i['surface_m2'] for i in diam_infos)

        if started:
            first_activity = diam_first_activity.get(dk, prod_start)
            diam_elapsed = max(1, (today - first_activity).days)
            actual_rate = done_hrs / diam_elapsed
            forecast_days = remaining_hrs / actual_rate if actual_rate > 0 else 999
            forecast_end = today + timedelta(days=max(1, int(forecast_days + 0.5)))
        elif avg_rate:
            forecast_days = total_hrs / avg_rate
            latest_start = committed_end - timedelta(days=int(forecast_days + 0.5))
            if today <= latest_start:
                forecast_end = committed_end; forecast_days = (committed_end - today).days
            else:
                forecast_end = today + timedelta(days=max(1, int(forecast_days + 0.5)))
        else:
            forecast_end = committed_end; forecast_days = (committed_end - today).days

        if forecast_end < committed_end:
            forecast_end = committed_end; forecast_days = (committed_end - today).days

        fc_result[dk] = {
            'phase_avgs': phase_avgs,
            'overall_pct': round(overall_pct, 1), 'forecast_end': str(forecast_end),
            'forecast_days': round(forecast_days, 1),
            'total_hrs': round(total_hrs, 1), 'done_hrs': round(done_hrs, 1),
            'remaining_hrs': round(remaining_hrs, 1),
            'remaining_raf': round(remaining_raf, 0), 'remaining_m2': round(remaining_m2, 1),
            'total_raf': round(total_raf, 0), 'total_m2': round(total_m2, 1),
            'spool_count': len(diam_infos), 'started': started,
        }
        if forecast_end and (overall_forecast is None or forecast_end > overall_forecast):
            overall_forecast = forecast_end

    return {
        'diameters': fc_result, 'overall_forecast_end': str(overall_forecast) if overall_forecast else None,
        'today': str(today), 'welding_capability': weld_cap, 'painting_capability': paint_cap,
        'actual_weld_ipd': actual_weld_ipd, 'actual_paint_m2d': actual_paint_m2d,
        'days_elapsed': global_days_elapsed,
    }

def past_hold_point_count(project):
    """Count spools that have passed the hold point (RT or equivalent)."""
    steps_def = get_project_steps(project)
    hold_steps = [s['step_number'] for s in steps_def if s.get('is_hold_point')]
    if not hold_steps: return 0
    hs = hold_steps[0]
    row = db_fetchone("SELECT COUNT(*) as cnt FROM progress WHERE project=? AND step_number=? AND completed=1", (project, hs))
    return row['cnt'] if row else 0

def daily_production_rate(project):
    """Calculate 7-day average production rate and today's steps."""
    today = date.today()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)
    if USE_PG:
        this_week_spools = db_fetchall("SELECT COUNT(DISTINCT spool_id) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp::date >= ?::date AND timestamp::date <= ?::date", (project, str(week_ago), str(today)))
        last_week_spools = db_fetchall("SELECT COUNT(DISTINCT spool_id) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp::date >= ?::date AND timestamp::date < ?::date", (project, str(two_weeks_ago), str(week_ago)))
        today_steps = db_fetchall("SELECT COUNT(*) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp::date = ?::date", (project, str(today)))
        today_spools = db_fetchall("SELECT COUNT(DISTINCT spool_id) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp::date = ?::date", (project, str(today)))
    else:
        this_week_spools = db_fetchall("SELECT COUNT(DISTINCT spool_id) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp >= ? AND timestamp <= ?", (project, str(week_ago), str(today) + ' 23:59:59'))
        last_week_spools = db_fetchall("SELECT COUNT(DISTINCT spool_id) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp >= ? AND timestamp < ?", (project, str(two_weeks_ago), str(week_ago)))
        today_steps = db_fetchall("SELECT COUNT(*) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp LIKE ?", (project, str(today) + '%'))
        today_spools = db_fetchall("SELECT COUNT(DISTINCT spool_id) as cnt FROM activity_log WHERE project=? AND action='completed' AND timestamp LIKE ?", (project, str(today) + '%'))
    this_wk = this_week_spools[0]['cnt'] if this_week_spools else 0
    last_wk = last_week_spools[0]['cnt'] if last_week_spools else 0
    today_cnt = today_steps[0]['cnt'] if today_steps else 0
    today_sp = today_spools[0]['cnt'] if today_spools else 0
    avg_7day = round(this_wk / 7, 1)
    avg_prev = round(last_wk / 7, 1)
    trend = round(avg_7day - avg_prev, 1)
    return {'avg_7day': avg_7day, 'avg_prev_week': avg_prev, 'trend': trend, 'today_steps': today_cnt, 'today_spools': today_sp}

def generate_report_data(project):
    """Build full report data for a project."""
    settings = get_project_settings(project)
    steps_def = get_project_steps(project)
    bulk = bulk_spool_progress(project, settings)
    st = project_stats(project)
    sched = schedule_status(project, bulk)
    forecast = forecast_production(project, bulk)
    today = date.today().strftime('%Y-%m-%d')
    today_act = daily_activity(project, today)
    steps_today = len([a for a in today_act if a.get('action') == 'completed'])
    # Dynamic release step detection
    release_steps = {s['step_number'] for s in steps_def if s.get('is_release')}
    hold_steps = {s['step_number'] for s in steps_def if s.get('is_hold_point')}
    released_today = len([a for a in today_act if a.get('action') == 'completed' and a.get('step_number') in release_steps])
    rt_count = past_hold_point_count(project)
    prod_rate = daily_production_rate(project)
    spool_pcts = {sid: info['pct'] for sid, info in bulk.items()}
    step_names = {s['step_number']: s['name_en'] for s in steps_def}
    completed_spools = [sid for sid, info in bulk.items() if info['pct'] >= 100]
    return {
        'project': project, 'date': today, 'stats': st, 'schedule': sched,
        'today_activity': today_act, 'steps_completed_today': steps_today,
        'completed_spools': completed_spools, 'total_spools': len(bulk),
        'settings': settings, 'forecast': forecast, 'past_rt': rt_count,
        'production_rate': prod_rate, 'spool_progress': spool_pcts,
        'step_names': step_names, 'released_today': released_today,
        'hold_steps': list(hold_steps), 'release_steps': list(release_steps),
        'phase_order': get_phase_order(steps_def),
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
    import traceback as tb
    try:
        settings = get_project_settings(project)
        bulk = bulk_spool_progress(project, settings)
        st = project_stats(project)
        act = db_fetchall("SELECT * FROM activity_log WHERE project=? ORDER BY timestamp DESC LIMIT 20", (project,))
        st['recent_activity'] = fix_timestamps(act)
        st['settings'] = settings
        st['forecast'] = forecast_production(project, bulk)
        st['past_rt'] = past_hold_point_count(project)
        st['production_rate'] = daily_production_rate(project)
        st['schedule_data'] = schedule_status(project, bulk)
        return jsonify(st)
    except Exception as e:
        print(f"Dashboard error: {e}\n{tb.format_exc()}")
        return jsonify({'error': str(e), 'trace': tb.format_exc()}), 500

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
    steps_def = get_project_steps(project)
    steps = fix_timestamps(db_fetchall("SELECT * FROM progress WHERE project=? AND spool_id=? ORDER BY step_number", (project, spool_id)))
    act = fix_timestamps(db_fetchall("SELECT * FROM activity_log WHERE project=? AND spool_id=? ORDER BY timestamp DESC LIMIT 10", (project, spool_id)))
    step_definitions = [
        {'number':s['step_number'],'name_en':s['name_en'],'name_cn':s['name_cn'],'weight':s['weight'],
         'is_hold_point':s.get('is_hold_point',0),'is_release':s.get('is_release',0)}
        for s in steps_def
        if not s['is_conditional'] or sp.get('has_branches')
    ]
    return jsonify({'spool':sp, 'progress_pct': spool_progress(project, spool_id), 'steps':steps, 'activity':act,
        'step_definitions': step_definitions,
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
    steps_def = get_project_steps(project)
    sn = next((s['name_en'] for s in steps_def if s['step_number']==step), f"Step {step}")
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
            spool_type = s.get('spool_type', 'SPOOL') or 'SPOOL'
            if USE_PG:
                db_execute("INSERT INTO spools (project,spool_id,spool_full,iso_no,marking,mk_number,main_diameter,line,sequence,has_branches,spool_type) VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT (project,spool_id) DO UPDATE SET has_branches=EXCLUDED.has_branches, spool_type=EXCLUDED.spool_type",
                    (proj, s['spool_id'], s.get('spool_full',''), s.get('iso_no',''), s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''), s.get('line',''), s.get('sequence',0), 1 if s.get('has_branches') else 0, spool_type))
            else:
                db_execute("INSERT INTO spools (project,spool_id,spool_full,iso_no,marking,mk_number,main_diameter,line,sequence,has_branches,spool_type) VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(project,spool_id) DO UPDATE SET has_branches=excluded.has_branches, spool_type=excluded.spool_type",
                    (proj, s['spool_id'], s.get('spool_full',''), s.get('iso_no',''), s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''), s.get('line',''), s.get('sequence',0), 1 if s.get('has_branches') else 0, spool_type))
            has_br = 1 if s.get('has_branches') else 0
            steps_def = get_project_steps(proj)
            for step in steps_def:
                if step['is_conditional'] and not has_br:
                    continue
                st = step.get('spool_type', 'ALL') or 'ALL'
                if st != 'ALL' and st != spool_type:
                    continue
                if USE_PG:
                    db_execute("INSERT INTO progress (project,spool_id,step_number,completed) VALUES (?,?,?,0) ON CONFLICT (project,spool_id,step_number) DO NOTHING", (proj, s['spool_id'], step['step_number']))
                else:
                    db_execute("INSERT OR IGNORE INTO progress (project,spool_id,step_number,completed) VALUES (?,?,?,0)", (proj, s['spool_id'], step['step_number']))
            count += 1
        except Exception as e: print(f"Import error {s.get('spool_id','?')}: {e}")
    db_commit()
    return jsonify({'ok':True, 'imported':count})

@app.route('/api/project/<project>/export')
@login_required
def api_export(project):
    import openpyxl; from openpyxl.styles import Font, PatternFill, Alignment; import tempfile
    steps_def = get_project_steps(project)
    spools = db_fetchall("SELECT * FROM spools WHERE project=? ORDER BY sequence", (project,))
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = project
    hdr = ['#','Spool','Diameter','Line','Progress %'] + [f"S{s['step_number']}" for s in steps_def]
    hf = Font(bold=True,size=9,color='FFFFFF'); hfill = PatternFill(start_color='2F5496',end_color='2F5496',fill_type='solid')
    for c,h in enumerate(hdr,1):
        cl = ws.cell(1,c,h); cl.font=hf; cl.fill=hfill; cl.alignment=Alignment(horizontal='center',wrap_text=True)
    for i,s in enumerate(spools,2):
        p = spool_progress(project, s['spool_id'])
        steps = db_fetchall("SELECT step_number,completed FROM progress WHERE project=? AND spool_id=?", (project, s['spool_id']))
        sm = {st['step_number']:st['completed'] for st in steps}
        ws.cell(i,1,i-1); ws.cell(i,2,s['spool_id']); ws.cell(i,3,s['main_diameter']); ws.cell(i,4,s['line']); ws.cell(i,5,p)
        for j,sd in enumerate(steps_def):
            c = 6+j; done = sm.get(sd['step_number'],0)
            ws.cell(i,c,'\u2713' if done else '')
            if done: ws.cell(i,c).fill = PatternFill(start_color='C6EFCE',end_color='C6EFCE',fill_type='solid')
    ws.column_dimensions['B'].width=15; ws.freeze_panes='A2'
    tmp = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False); wb.save(tmp.name)
    return send_file(tmp.name, as_attachment=True, download_name=f"{project}_progress_{date.today().strftime('%Y%m%d')}.xlsx")

@app.route('/api/project/<project>/spool/<spool_id>/weight', methods=['POST'])
@login_required
def api_update_weight(project, spool_id):
    d = request.get_json() or {}
    weight = d.get('weight_kg', 0); op = d.get('operator', '')
    db_execute("UPDATE spools SET actual_weight_kg=? WHERE project=? AND spool_id=?", (weight, project, spool_id))
    db_execute("INSERT INTO activity_log (project,spool_id,step_number,action,operator,details) VALUES (?,?,?,?,?,?)",
        (project, spool_id, 0, 'weight', op, f"Weight recorded: {weight} kg by {op}"))
    db_commit()
    return jsonify({'ok': True, 'weight_kg': weight})

@app.route('/api/project/<project>/surface', methods=['POST'])
def api_bulk_surface(project):
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON'}), 400
    count = 0
    for spool_id, surface in data.items():
        db_execute("UPDATE spools SET surface_m2=? WHERE project=? AND spool_id=?", (float(surface), project, spool_id))
        count += 1
    db_commit()
    return jsonify({'ok': True, 'updated': count})

@app.route('/api/project/<project>/joints', methods=['POST'])
def api_bulk_joints(project):
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON'}), 400
    count = 0
    for spool_id, vals in data.items():
        jc = vals.get('joint_count', 0) if isinstance(vals, dict) else int(vals)
        ri = vals.get('raf_inches', 0) if isinstance(vals, dict) else 0
        db_execute("UPDATE spools SET joint_count=?, raf_inches=? WHERE project=? AND spool_id=?", (jc, ri, project, spool_id))
        count += 1
    db_commit()
    return jsonify({'ok': True, 'updated': count})

@app.route('/api/project/<project>/spool/<spool_id>/drawing', methods=['POST'])
def api_upload_drawing(project, spool_id):
    if 'file' in request.files: pdf_data = request.files['file'].read()
    else: pdf_data = request.get_data()
    if not pdf_data: return jsonify({'error': 'No data'}), 400
    if USE_PG:
        import psycopg2
        db_execute("DELETE FROM drawings WHERE project=%s AND spool_id=%s", (project, spool_id))
        cur = get_db().cursor()
        cur.execute("INSERT INTO drawings (project, spool_id, pdf_data) VALUES (%s, %s, %s)", (project, spool_id, psycopg2.Binary(pdf_data)))
    else:
        db_execute("DELETE FROM drawings WHERE project=? AND spool_id=?", (project, spool_id))
        db_execute("INSERT INTO drawings (project, spool_id, pdf_data) VALUES (?,?,?)", (project, spool_id, pdf_data))
    db_commit()
    return jsonify({'ok': True, 'size_kb': round(len(pdf_data)/1024, 1)})

@app.route('/api/project/<project>/spool/<spool_id>/drawing')
@login_required
def api_get_drawing(project, spool_id):
    if USE_PG:
        cur = get_db().cursor()
        cur.execute("SELECT pdf_data FROM drawings WHERE project=%s AND spool_id=%s", (project, spool_id))
        row = cur.fetchone()
        if not row: return jsonify({'error': 'No drawing'}), 404
        pdf_data = bytes(row[0])
    else:
        row = db_fetchone("SELECT pdf_data FROM drawings WHERE project=? AND spool_id=?", (project, spool_id))
        if not row: return jsonify({'error': 'No drawing'}), 404
        pdf_data = row['pdf_data']
    from flask import Response
    return Response(pdf_data, mimetype='application/pdf', headers={'Content-Disposition': f'inline; filename={spool_id}.pdf'})

@app.route('/api/project/<project>/drawings/list')
@login_required
def api_list_drawings(project):
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
    results = []
    try:
        if USE_PG:
            # Add columns/tables that might be missing on older deployments
            for col, tbl, default in [
                ('has_branches', 'spools', '0'), ('actual_weight_kg', 'spools', '0'),
                ('surface_m2', 'spools', '0'), ('joint_count', 'spools', '0'),
                ('raf_inches', 'spools', '0'), ('spool_type', 'spools', "'SPOOL'"),
            ]:
                try:
                    db_execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {'INTEGER' if col in ('has_branches','joint_count') else 'REAL' if col in ('actual_weight_kg','surface_m2','raf_inches') else 'TEXT'} DEFAULT {default}")
                    results.append(f"added {col}")
                except: get_db().rollback(); results.append(f"{col} exists")
        db_commit(); results.append("migration complete")
    except Exception as e: results.append(str(e))
    return jsonify({'ok': True, 'results': results})

@app.route('/api/project/<project>/spool/<spool_id>/delete', methods=['POST'])
def api_delete_spool(project, spool_id):
    db_execute("DELETE FROM activity_log WHERE project=? AND spool_id=?", (project, spool_id))
    db_execute("DELETE FROM progress WHERE project=? AND spool_id=?", (project, spool_id))
    db_execute("DELETE FROM drawings WHERE project=? AND spool_id=?", (project, spool_id))
    db_execute("DELETE FROM spools WHERE project=? AND spool_id=?", (project, spool_id))
    db_commit()
    return jsonify({'ok': True, 'deleted': spool_id})

@app.route('/api/cleanup', methods=['POST'])
def api_cleanup():
    db_execute("DELETE FROM activity_log WHERE project=''")
    db_execute("DELETE FROM progress WHERE project=''")
    db_execute("DELETE FROM spools WHERE project=''")
    db_execute("DELETE FROM drawings WHERE NOT EXISTS (SELECT 1 FROM spools WHERE spools.project=drawings.project AND spools.spool_id=drawings.spool_id)")
    db_commit()
    return jsonify({'ok': True})

@app.route('/healthz')
def healthz():
    try: db_execute("SELECT 1"); return jsonify({'status':'ok','db':'connected'})
    except Exception as e: return jsonify({'status':'error','db':str(e)}), 500

# ── API: Project Steps ────────────────────────────────────────────────────────
@app.route('/api/project/<project>/steps', methods=['GET', 'POST'])
def api_project_steps(project):
    """Get or set ITP step definitions for a project."""
    if request.method == 'GET':
        steps = get_project_steps(project)
        return jsonify(steps)
    data = request.get_json()
    if not data or not isinstance(data, list): return jsonify({'error': 'Expected JSON array of step definitions'}), 400
    db_execute("DELETE FROM project_steps WHERE project=?", (project,))
    for s in data:
        if USE_PG:
            db_execute("INSERT INTO project_steps (project,step_number,name_en,name_cn,weight,category,hours_fixed,hours_variable,spool_type,display_order,is_conditional,is_hold_point,is_release,phase) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (project, s['step_number'], s['name_en'], s.get('name_cn',''), s.get('weight',5), s['category'],
                 s.get('hours_fixed',2.0), s.get('hours_variable',''), s.get('spool_type','ALL'),
                 s['display_order'], s.get('is_conditional',0), s.get('is_hold_point',0), s.get('is_release',0), s.get('phase','fab')))
        else:
            db_execute("INSERT INTO project_steps (project,step_number,name_en,name_cn,weight,category,hours_fixed,hours_variable,spool_type,display_order,is_conditional,is_hold_point,is_release,phase) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (project, s['step_number'], s['name_en'], s.get('name_cn',''), s.get('weight',5), s['category'],
                 s.get('hours_fixed',2.0), s.get('hours_variable',''), s.get('spool_type','ALL'),
                 s['display_order'], s.get('is_conditional',0), s.get('is_hold_point',0), s.get('is_release',0), s.get('phase','fab')))
    db_commit()
    # Clear cache
    cache_key = f'_steps_{project}'
    if hasattr(g, cache_key): delattr(g, cache_key)
    return jsonify({'ok': True, 'steps': len(data)})

# ── API: Schedule & Reports ──────────────────────────────────────────────────
@app.route('/api/project/<project>/schedule', methods=['POST'])
def api_set_schedule(project):
    """Import schedule data. Accepts JSON array or {start: 'YYYY-MM-DD'} for auto-calculation."""
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON data'}), 400
    count = 0
    if isinstance(data, list):
        for item in data:
            if USE_PG:
                db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (project,diameter,task_type) DO UPDATE SET description=EXCLUDED.description,planned_start=EXCLUDED.planned_start,planned_end=EXCLUDED.planned_end,spool_count=EXCLUDED.spool_count",
                    (project, item['diameter'], item['task_type'], item.get('description',''), item['planned_start'], item['planned_end'], item.get('spool_count',0)))
            else:
                db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (?,?,?,?,?,?,?) ON CONFLICT(project,diameter,task_type) DO UPDATE SET description=excluded.description,planned_start=excluded.planned_start,planned_end=excluded.planned_end,spool_count=excluded.spool_count",
                    (project, item['diameter'], item['task_type'], item.get('description',''), item['planned_start'], item['planned_end'], item.get('spool_count',0)))
            count += 1
    elif isinstance(data, dict) and ('start' in data or 'fab_start' in data):
        start_date = date.fromisoformat(data.get('start', data.get('fab_start')))
        settings = get_project_settings(project)
        steps_def = get_project_steps(project)
        phase_order = get_phase_order(steps_def)
        std_weeks = int(settings.get('standard_weeks', '9'))
        secondary_phase_days = int(settings.get('secondary_phase_days', '13'))
        diam_order = get_diameter_order(project)
        spools_rows = db_fetchall("SELECT main_diameter FROM spools WHERE project=?", (project,))
        diam_counts = {}
        for s in spools_rows:
            d = (s['main_diameter'] or '?').replace('"','')
            if d == '?' or d == '0' or d == '': continue
            if d not in diam_counts: diam_counts[d] = 0
            diam_counts[d] += 1
        total_spools = sum(diam_counts.values())
        # Standard schedule: proportional distribution across standard_weeks
        # One diameter at a time, largest first, each gets (count/total) share of total days
        total_std_days = std_weeks * 7
        # For multi-phase: first phase gets (total_std_days - secondary_phase_days), second phase gets secondary_phase_days per diameter
        if len(phase_order) > 1:
            first_phase_total_days = total_std_days - secondary_phase_days  # last diameter's paint must finish by end
        else:
            first_phase_total_days = total_std_days  # single phase uses all days
        current_start = start_date
        remaining_days = first_phase_total_days
        first_phase = phase_order[0] if phase_order else 'fab'
        for i, diam in enumerate(diam_order):
            if diam not in diam_counts: continue
            cnt = diam_counts[diam]
            # Proportional: this diameter gets its share of total days
            if total_spools > 0:
                if i == len([d for d in diam_order if d in diam_counts]) - 1:
                    fab_days = remaining_days  # last diameter gets remainder
                else:
                    fab_days = max(1, round(first_phase_total_days * cnt / total_spools))
            else:
                fab_days = 1
            remaining_days -= fab_days
            fab_end = current_start + timedelta(days=fab_days)
            dk = f'{diam}"'
            phase_entries = []
            phase_entries.append((first_phase, current_start, fab_end, f'{first_phase.capitalize()} {dk} ({cnt} spools)'))
            # Secondary phases follow immediately after first phase for this diameter
            prev_end = fab_end
            for ph in phase_order[1:]:
                ph_start = prev_end + timedelta(days=1)
                ph_end = ph_start + timedelta(days=secondary_phase_days)
                phase_entries.append((ph, ph_start, ph_end, f'{ph.capitalize()} {dk}'))
                prev_end = ph_end
            current_start = fab_end  # next diameter starts when this one's first phase ends
            for tt, sd, ed, desc in phase_entries:
                if USE_PG:
                    db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (project,diameter,task_type) DO UPDATE SET description=EXCLUDED.description,planned_start=EXCLUDED.planned_start,planned_end=EXCLUDED.planned_end,spool_count=EXCLUDED.spool_count",
                        (project, dk, tt, desc, str(sd), str(ed), cnt))
                else:
                    db_execute("INSERT INTO schedule (project,diameter,task_type,description,planned_start,planned_end,spool_count) VALUES (?,?,?,?,?,?,?) ON CONFLICT(project,diameter,task_type) DO UPDATE SET description=excluded.description,planned_start=excluded.planned_start,planned_end=excluded.planned_end,spool_count=excluded.spool_count",
                        (project, dk, tt, desc, str(sd), str(ed), cnt))
                count += 1
    db_commit()
    return jsonify({'ok': True, 'entries': count})

@app.route('/api/project/<project>/schedule')
@login_required
def api_get_schedule(project):
    rows = db_fetchall("SELECT * FROM schedule WHERE project=? ORDER BY planned_start", (project,))
    return jsonify(fix_timestamps(rows))

@app.route('/api/project/<project>/settings', methods=['GET','POST'])
def api_project_settings(project):
    if request.method == 'GET':
        return jsonify(get_project_settings(project))
    data = request.get_json()
    if not data: return jsonify({'error':'No JSON'}), 400
    for k, v in data.items():
        if USE_PG:
            db_execute("INSERT INTO project_settings (project,key,value) VALUES (%s,%s,%s) ON CONFLICT (project,key) DO UPDATE SET value=EXCLUDED.value", (project, k, str(v)))
        else:
            db_execute("INSERT INTO project_settings (project,key,value) VALUES (?,?,?) ON CONFLICT(project,key) DO UPDATE SET value=excluded.value", (project, k, str(v)))
    db_commit()
    return jsonify({'ok': True, 'settings': get_project_settings(project)})

@app.route('/api/project/<project>/report')
@login_required
def api_report_data(project):
    import traceback as tb
    try:
        return jsonify(generate_report_data(project))
    except Exception as e:
        print(f"Report error: {e}\n{tb.format_exc()}")
        return jsonify({'error': str(e), 'trace': tb.format_exc()}), 500

@app.route('/project/<project>/report')
@login_required
def report_page(project):
    return render_template_string(REPORT_HTML, project=project)

@app.route('/api/project/<project>/report/download')
@login_required
def api_report_download(project):
    """Download a professional Excel production report."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    import tempfile
    rpt = generate_report_data(project)
    st = rpt['stats']; sched = rpt.get('schedule'); sett = rpt.get('settings', {})
    fc_data = rpt.get('forecast', {}) or {}
    fc_diams = fc_data.get('diameters', {}) if fc_data else {}
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Production Report"
    hf = Font(bold=True, size=11, color='FFFFFF'); hfill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    dark_fill = PatternFill(start_color='404040', end_color='404040', fill_type='solid')
    bf = Font(size=10); bfb = Font(bold=True, size=10)
    green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    orange_fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
    red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
    thin = Border(left=Side('thin',color='C0C0C0'),right=Side('thin',color='C0C0C0'),top=Side('thin',color='C0C0C0'),bottom=Side('thin',color='C0C0C0'))
    center = Alignment(horizontal='center', vertical='center')
    std_weeks = int(sett.get('standard_weeks', '9'))
    wks_saved = int(sett.get('committed_weeks_saved', '0'))
    days_saved = int(sett.get('committed_days_saved', '0'))
    total_saved = wks_saved * 7 + days_saved
    has_expediting = total_saved > 0
    transit_days = int(sett.get('sea_transit_days', '45'))
    today = date.today()
    ws.merge_cells('A1:H1')
    ws['A1'] = f"ENERXON \u2014 Production Report / \u751f\u4ea7\u62a5\u544a"; ws['A1'].font = Font(bold=True, size=16, color='2F5496')
    ws['A2'] = f"Project: {project}"; ws['A2'].font = bfb
    ws['A3'] = f"Date: {rpt['date']}"; ws['A3'].font = bf
    ws['A4'] = f"Overall Progress: {st['overall_pct']}%"; ws['A4'].font = Font(bold=True, size=14, color='2F5496')
    ws['A5'] = f"Total: {st['total']} spools | Done: {st['completed']} | In Progress: {st['in_progress']} | Pending: {st['not_started']}"; ws['A5'].font = bf
    row = 7
    if sched and sched.get('diameters'):
        status_label = {'on_time': 'ON TIME \u2713', 'at_risk': 'AT RISK \u26a0', 'delayed': 'DELAYED \u2717', 'not_started': 'NOT STARTED'}
        ws.cell(row, 1, "SCHEDULE STATUS BY DIAMETER / \u6309\u7ba1\u5f84\u8ba1\u5212\u72b6\u6001").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        phases = sched.get('phase_order', ['fab'])
        phase_colors = ['4472C4', 'ED7D31', '8E44AD', '27AE60']
        phase_headers = [f'{ph.capitalize()} %' for ph in phases]
        headers = ['Diameter','Spools'] + phase_headers + ['Overall %','Diff (days)','Status','Start','End','Forecast End']
        for col, h in enumerate(headers, 1):
            c = ws.cell(row, col, h); c.font = hf; c.fill = hfill; c.alignment = Alignment(horizontal='center', wrap_text=True); c.border = thin
        row += 1
        for d in sched['diameters']:
            dk = d['diameter']; fcd = fc_diams.get(dk, {})
            ws.cell(row, 1, dk).font = bfb; ws.cell(row, 1).border = thin
            ws.cell(row, 2, d['spool_count']).font = bf; ws.cell(row, 2).alignment = center; ws.cell(row, 2).border = thin
            col_idx = 3
            for ph in phases:
                ph_val = (d.get('phase_avgs') or {}).get(ph, 0)
                cp = ws.cell(row, col_idx, ph_val); cp.font = bfb; cp.alignment = center; cp.border = thin
                if ph_val >= 100: cp.fill = green_fill
                col_idx += 1
            ws.cell(row, col_idx, d['actual_pct']).font = bfb; ws.cell(row, col_idx).alignment = center; ws.cell(row, col_idx).border = thin
            col_idx += 1
            diff_val = d['diff']; diff_label = f"+{diff_val}d" if diff_val > 0 else f"{diff_val}d" if diff_val < 0 else "0d"
            c6 = ws.cell(row, col_idx, diff_label); c6.alignment = center; c6.border = thin
            c6.font = Font(size=10, color='27AE60' if diff_val > 0 else 'E74C3C' if diff_val < 0 else '333333')
            col_idx += 1
            sc = ws.cell(row, col_idx, status_label.get(d['status'], d['status']))
            sc.font = bfb; sc.alignment = center; sc.border = thin
            if d['status'] == 'on_time': sc.fill = green_fill
            elif d['status'] == 'at_risk': sc.fill = orange_fill
            elif d['status'] == 'delayed': sc.fill = red_fill
            col_idx += 1
            ws.cell(row, col_idx, d.get('total_start','')).font = bf; ws.cell(row, col_idx).border = thin
            col_idx += 1
            ws.cell(row, col_idx, d.get('total_end','')).font = bf; ws.cell(row, col_idx).border = thin
            col_idx += 1
            ws.cell(row, col_idx, fcd.get('forecast_end', '')).font = bf; ws.cell(row, col_idx).border = thin
            row += 1
        row += 1
        # Expediting + Gantt + Rate + Results + Transit — same as before
        prod_start = None
        starts = [d['total_start'] for d in sched['diameters'] if d.get('total_start')]
        if starts: prod_start = date.fromisoformat(min(starts))
        if prod_start and has_expediting:
            std_end = prod_start + timedelta(days=std_weeks * 7 - 1)
            commit_end = std_end - timedelta(days=total_saved)
            fc_overall_end = fc_data.get('overall_forecast_end')
            fc_end_d = date.fromisoformat(fc_overall_end) if fc_overall_end else None
            fc_diff_commit = (commit_end - fc_end_d).days if fc_end_d else 0
            commit_fill = PatternFill(start_color='D9E2F3', end_color='D9E2F3', fill_type='solid')
            ws.cell(row, 1, "\u26a1 EXPEDITING COMMITMENT / \u52a0\u6025\u627f\u8bfa").font = Font(bold=True, size=12, color='4472C4')
            row += 1
            commit_items = [
                ('Start / \u5f00\u59cb', str(prod_start), '2F5496'),
                ('Standard End / \u6807\u51c6\u5b8c\u5de5', str(std_end), '888888'),
                ('Committed End / \u627f\u8bfa\u5b8c\u5de5', str(commit_end), '4472C4'),
                ('Saved / \u8282\u7701', f"{total_saved} days ({wks_saved} weeks)", '4472C4'),
                ('Forecast / \u9884\u6d4b', "{} {}".format(fc_end_d or '\u2014', '\u2713' if fc_diff_commit >= 0 else '\u2717'), '27AE60' if fc_diff_commit >= 0 else 'E74C3C'),
            ]
            for ci, (label, val, color) in enumerate(commit_items):
                c1 = ws.cell(row, ci*2 + 1, label); c1.font = Font(size=9, color='666666'); c1.fill = commit_fill; c1.border = thin
                c2 = ws.cell(row, ci*2 + 2, val); c2.font = Font(bold=True, size=11, color=color); c2.fill = commit_fill; c2.border = thin
            row += 2
        elif prod_start:
            std_end = prod_start + timedelta(days=std_weeks * 7 - 1)
            commit_end = std_end; fc_end_d = None
        else:
            std_end = None; commit_end = None; fc_end_d = None
        # Gantt
        ws.cell(row, 1, "PRODUCTION GANTT / \u751f\u4ea7\u7518\u7279\u56fe").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        if prod_start:
            fc_overall_end = fc_data.get('overall_forecast_end')
            if not fc_end_d and fc_overall_end: fc_end_d = date.fromisoformat(fc_overall_end)
            if has_expediting: num_weeks = std_weeks
            else:
                max_d = std_end or prod_start + timedelta(days=62)
                if fc_end_d and fc_end_d > max_d: max_d = fc_end_d
                num_weeks = max(std_weeks, ((max_d - prod_start).days // 7) + 2)
            weeks = []
            for i in range(num_weeks):
                ws_date = prod_start + timedelta(days=i * 7); we_date = ws_date + timedelta(days=6)
                weeks.append((ws_date, we_date))
            ratio = (std_weeks - wks_saved) / std_weeks if has_expediting else 1.0
            gantt_hdr_row = row
            ws.cell(row, 1, 'Diameter').font = Font(bold=True, size=9, color='FFFFFF'); ws.cell(row, 1).fill = dark_fill; ws.cell(row, 1).border = thin
            ws.cell(row, 2, 'Phase').font = Font(bold=True, size=9, color='FFFFFF'); ws.cell(row, 2).fill = dark_fill; ws.cell(row, 2).border = thin
            ws.cell(row, 3, '%').font = Font(bold=True, size=9, color='FFFFFF'); ws.cell(row, 3).fill = dark_fill; ws.cell(row, 3).alignment = center; ws.cell(row, 3).border = thin
            today_col = None
            for i, (ws_d, we_d) in enumerate(weeks):
                col = 4 + i; wk_label = f"W{i+1}\n{ws_d.strftime('%d/%m')}"
                c = ws.cell(row, col, wk_label)
                is_current = ws_d <= today <= we_d
                if is_current: c.fill = PatternFill(start_color='C00000', end_color='C00000', fill_type='solid'); today_col = col
                else: c.fill = dark_fill
                c.font = Font(bold=True, size=7, color='FFFFFF'); c.alignment = Alignment(horizontal='center', wrap_text=True); c.border = thin
                ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 5.5
            row += 1
            phase_fills = [PatternFill(start_color=c, end_color=c, fill_type='solid') for c in phase_colors[:len(phases)]]
            saved_fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
            forecast_fill = PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid')
            today_border = Border(left=Side('thick',color='FF0000'),right=Side('thick',color='FF0000'),top=Side('thin',color='C0C0C0'),bottom=Side('thin',color='C0C0C0'))
            today_bar_border = Border(left=Side('thick',color='FF0000'),right=Side('thick',color='FF0000'),top=Side('medium',color='333333'),bottom=Side('medium',color='333333'))
            for d in sched['diameters']:
                dk = d['diameter']; fcd = fc_diams.get(dk, {})
                overall_pct = fcd.get('overall_pct', 0) or 0; dm_started = fcd.get('started', False)
                dm_fc_end_str = fcd.get('forecast_end', ''); dm_fc_end = date.fromisoformat(dm_fc_end_str) if dm_fc_end_str else None
                # Get phase percentages from phase_avgs
                dm_phase_avgs = fcd.get('phase_avgs', {}) or d.get('phase_avgs', {}) or {}
                # Parse schedule dates from phase_dates
                phase_dates = {}
                d_phase_dates = d.get('phase_dates', {})
                for ph in phases:
                    pd = d_phase_dates.get(ph, {})
                    if pd.get('start') and pd.get('end'):
                        phase_dates[ph] = (date.fromisoformat(pd['start']), date.fromisoformat(pd['end']))
                # Compute expedited dates per phase
                exp_phase_dates = {}
                prev_exp_end = None
                for pi, ph in enumerate(phases):
                    if ph not in phase_dates: continue
                    ph_ps, ph_pe = phase_dates[ph]
                    if has_expediting and commit_end:
                        exp_s = prod_start + timedelta(days=(ph_ps - prod_start).days * ratio)
                        exp_e = prod_start + timedelta(days=(ph_pe - prod_start).days * ratio)
                        if exp_e > commit_end: exp_e = commit_end
                        if prev_exp_end and exp_s < prev_exp_end: exp_s = prev_exp_end
                        if exp_e < exp_s: exp_e = exp_s
                    else:
                        exp_s = ph_ps; exp_e = ph_pe
                    exp_phase_dates[ph] = (exp_s, exp_e)
                    prev_exp_end = exp_e
                # Render one row per phase
                for pi, ph in enumerate(phases):
                    ph_pct = dm_phase_avgs.get(ph, 0) or 0
                    ph_color = phase_colors[pi % len(phase_colors)]
                    ph_fill = phase_fills[pi % len(phase_fills)]
                    is_first = pi == 0
                    # Diameter label only on first row
                    if is_first:
                        ws.cell(row, 1, dk).font = Font(bold=True, size=11, color='2F5496'); ws.cell(row, 1).border = thin
                    else:
                        ws.cell(row, 1, '').border = thin
                    ws.cell(row, 2, ph.capitalize()).font = Font(size=9, color='666666'); ws.cell(row, 2).border = thin
                    pct_cell = ws.cell(row, 3)
                    if ph_pct >= 100: pct_cell.value = '\u2713'; pct_cell.font = Font(bold=True, size=10, color='27AE60')
                    elif ph_pct > 0: pct_cell.value = f'{ph_pct:.0f}%'; pct_cell.font = Font(bold=True, size=8, color=ph_color)
                    else: pct_cell.value = '-'; pct_cell.font = Font(size=8, color='AAAAAA')
                    pct_cell.alignment = center; pct_cell.border = thin
                    if ph in phase_dates and ph in exp_phase_dates:
                        ph_ps, ph_pe = phase_dates[ph]
                        exp_s, exp_e = exp_phase_dates[ph]
                        is_last_phase = pi == len(phases) - 1
                        for i, (ws_d, we_d) in enumerate(weeks):
                            col = 4 + i; cell = ws.cell(row, col); cell.border = thin
                            in_std = ph_ps <= we_d and ph_pe >= ws_d
                            in_exp = exp_s <= we_d and exp_e >= ws_d
                            is_saved_cell = has_expediting and in_std and not in_exp
                            is_today_col = today_col and col == today_col
                            is_forecast = is_last_phase and dm_started and dm_fc_end and overall_pct < 100 and dm_fc_end >= ws_d and dm_fc_end <= we_d
                            if in_exp:
                                cell.fill = ph_fill
                                if is_today_col and 0 < ph_pct < 100: cell.value = f'{ph_pct:.0f}%'; cell.font = Font(bold=True, size=7, color='FFFFFF'); cell.alignment = center
                                elif ph_pct >= 100 and we_d < today: cell.value = '\u2713'; cell.font = Font(bold=True, size=8, color='FFFFFF'); cell.alignment = center
                            elif is_saved_cell:
                                cell.fill = saved_fill
                            elif is_forecast:
                                cell.fill = forecast_fill; cell.value = '\u25c6'; cell.font = Font(size=8, color='C00000'); cell.alignment = center
                            if is_today_col: cell.border = today_bar_border if in_exp else today_border
                    else:
                        for i in range(len(weeks)):
                            col = 4 + i; cell = ws.cell(row, col); cell.border = thin
                            if today_col and col == today_col: cell.border = today_border
                    row += 1
            row += 1
            ws.cell(row, 1, 'Legend:').font = Font(bold=True, size=9)
            legend_col = 2
            for pi, ph in enumerate(phases):
                lg = ws.cell(row, legend_col, ph.capitalize()); lg.fill = phase_fills[pi % len(phase_fills)]; lg.font = Font(size=8, color='FFFFFF'); lg.alignment = center
                legend_col += 1
            if has_expediting:
                lg = ws.cell(row, legend_col, 'Saved \u2713'); lg.fill = saved_fill; lg.font = Font(size=8, color='A9D18E'); lg.alignment = center
                legend_col += 1
            lg = ws.cell(row, legend_col, '\u25c6 Forecast'); lg.fill = forecast_fill; lg.font = Font(size=8, color='C00000'); lg.alignment = center
            legend_col += 1
            ws.cell(row, legend_col, '| Today |').font = Font(bold=True, size=8, color='FF0000')
            row += 2
        # Production Rate
        actual_weld = fc_data.get('actual_weld_ipd', 0) or 0
        actual_paint = fc_data.get('actual_paint_m2d', 0) or 0
        weld_cap = fc_data.get('welding_capability', 0) or 0
        paint_cap = fc_data.get('painting_capability', 0) or 0
        ws.cell(row, 1, "PRODUCTION RATE / \u751f\u4ea7\u7387").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        rate_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
        rate_items = [('Welding / \u710a\u63a5', actual_weld, weld_cap, 'linear inches/day')]
        # Only show surface rate if project has surface steps
        has_surface = any(s.get('hours_variable') == 'surface' for s in get_project_steps(project))
        if has_surface:
            surface_label = phases[-1].capitalize() if len(phases) > 1 else 'Surface'
            rate_items.append((f'{surface_label} / \u6d82\u88c5', actual_paint, paint_cap, 'm\u00b2/day'))
        for label, actual, target, unit in rate_items:
            c1 = ws.cell(row, 1, label); c1.font = Font(bold=True, size=10); c1.fill = rate_fill; c1.border = thin
            c2 = ws.cell(row, 2, actual); c2.font = Font(bold=True, size=12, color='27AE60' if actual >= target else 'E74C3C'); c2.alignment = center; c2.fill = rate_fill; c2.border = thin
            c3 = ws.cell(row, 3, f"/ {target}"); c3.font = Font(size=9, color='888888'); c3.fill = rate_fill; c3.border = thin
            c4 = ws.cell(row, 4, unit); c4.font = Font(size=9, color='888888'); c4.fill = rate_fill; c4.border = thin
            pct_of_target = min(actual / max(target, 1) * 100, 100) if target else 0
            c5 = ws.cell(row, 5, f"{pct_of_target:.0f}% of target"); c5.font = Font(size=9, color='27AE60' if actual >= target else 'E74C3C'); c5.fill = rate_fill; c5.border = thin
            row += 1
        row += 1
        # Results Summary
        ws.cell(row, 1, "RESULTS SUMMARY / \u7ed3\u679c\u6458\u8981").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        res_fill = PatternFill(start_color='D9E2F3', end_color='D9E2F3', fill_type='solid')
        res_dark = PatternFill(start_color='333333', end_color='333333', fill_type='solid')
        if has_expediting and std_end and commit_end:
            fc_saved = (std_end - fc_end_d).days if fc_end_d else 0
            fc_diff_c = (commit_end - fc_end_d).days if fc_end_d else 0
            res_green = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
            results = [
                ('Overall Progress / \u603b\u8fdb\u5ea6', f"{st['overall_pct']}%", f"{st['total']} spools \u00b7 {st['in_progress']} WIP", res_fill, '2F5496'),
                ('Production End / \u751f\u4ea7\u5b8c\u5de5', f"{str(std_end)} \u2192 {str(commit_end)}", 'Standard \u2192 Committed (Expediting)', res_fill, '4472C4'),
                ('Expediting / \u52a0\u6025\u627f\u8bfa', f"{total_saved} days saved", f"{wks_saved} weeks with expediting fee", res_green, '27AE60'),
                ('Forecast / \u751f\u4ea7\u9884\u6d4b', f"{fc_saved} days saved \u00b7 ends {fc_end_d or chr(8212)}", ('\u2713 ' + str(fc_diff_c) + 'd ahead of commitment' if fc_diff_c >= 0 else '\u2717 ' + str(abs(fc_diff_c)) + 'd behind commitment') if fc_end_d else '', res_green, '27AE60' if fc_diff_c >= 0 else 'E74C3C'),
            ]
        else:
            fc_end_d = date.fromisoformat(fc_data.get('overall_forecast_end')) if fc_data and fc_data.get('overall_forecast_end') else None
            results = [
                ('Overall Progress / \u603b\u8fdb\u5ea6', f"{st['overall_pct']}%", f"{st['total']} spools \u00b7 {st['in_progress']} WIP", res_fill, '2F5496'),
                ('Forecast End / \u9884\u6d4b\u5b8c\u5de5', str(fc_end_d or '\u2014'), 'Based on actual rate', res_fill, '4472C4'),
            ]
        for label, val, sub, fill, color in results:
            c1 = ws.cell(row, 1, label); c1.font = Font(bold=True, size=10); c1.fill = fill; c1.border = thin
            c2 = ws.cell(row, 2, val); c2.font = Font(bold=True, size=11, color=color); c2.fill = fill; c2.border = thin
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            c5 = ws.cell(row, 5, sub); c5.font = Font(size=9, color='888888'); c5.fill = fill; c5.border = thin
            row += 1
        c1 = ws.cell(row, 1, 'Actual End / \u5b9e\u9645\u5b8c\u5de5'); c1.font = Font(bold=True, size=10, color='FFFFFF'); c1.fill = res_dark; c1.border = thin
        actual_end_val = str(today) if st['completed'] >= st['total'] else '\u2014'
        c2 = ws.cell(row, 2, actual_end_val); c2.font = Font(bold=True, size=11, color='FFFFFF'); c2.fill = res_dark; c2.border = thin
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
        c5 = ws.cell(row, 5, 'Production complete' if st['completed'] >= st['total'] else 'Shown when complete'); c5.font = Font(size=9, color='AAAAAA'); c5.fill = res_dark; c5.border = thin
        row += 2
        # Transit
        if has_expediting and commit_end:
            commit_arrival = commit_end + timedelta(days=transit_days)
            fc_arrival = fc_end_d + timedelta(days=transit_days) if fc_end_d else None
            ship_fill = PatternFill(start_color='002060', end_color='002060', fill_type='solid')
            ws.cell(row, 1, "\U0001f6a2 SEA TRANSIT / \u6d77\u8fd0").font = Font(bold=True, size=12, color='002060')
            row += 1
            c1 = ws.cell(row, 1, f"~{transit_days} days transit"); c1.font = Font(bold=True, size=10, color='FFFFFF'); c1.fill = ship_fill; c1.border = thin
            c2 = ws.cell(row, 2, f"Committed arrival: {commit_arrival}"); c2.font = Font(size=10, color='FFFFFF'); c2.fill = ship_fill; c2.border = thin
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            if fc_arrival:
                c5 = ws.cell(row, 5, f"Forecast arrival: {fc_arrival}"); c5.font = Font(size=10, color='FFFFFF'); c5.fill = ship_fill; c5.border = thin
            row += 2
    # Today's Activity
    if rpt.get('today_activity'):
        ws.cell(row, 1, f"TODAY'S ACTIVITY ({rpt['date']}) / \u4eca\u65e5\u52a8\u6001").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        steps_today = rpt.get('steps_completed_today', 0)
        released = rpt.get('released_today', 0)
        past_rt = rpt.get('past_rt', 0)
        spools_touched = len(set(a.get('spool_id','') for a in rpt['today_activity']))
        ws.cell(row, 1, f"{steps_today} steps").font = Font(bold=True, size=11, color='2F5496'); ws.cell(row, 1).border = thin
        ws.cell(row, 2, f"{spools_touched} spools").font = Font(bold=True, size=11, color='2F5496'); ws.cell(row, 2).border = thin
        ws.cell(row, 3, f"{released} released").font = Font(bold=True, size=11, color='27AE60'); ws.cell(row, 3).border = thin
        ws.cell(row, 4, f"{past_rt} past RT").font = Font(bold=True, size=11, color='4472C4'); ws.cell(row, 4).border = thin
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
    ws.column_dimensions['A'].width = 22; ws.column_dimensions['B'].width = 12; ws.column_dimensions['C'].width = 8
    ws.freeze_panes = 'A7'
    tmp = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False); wb.save(tmp.name)
    return send_file(tmp.name, as_attachment=True, download_name=f"{project}_report_{today.strftime('%Y%m%d')}.xlsx")

@app.route('/api/project/<project>/report/pdf')
@login_required
def api_report_pdf(project):
    """Download a professional PDF production report (landscape A4)."""
    import tempfile
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm, inch
    from reportlab.lib.colors import HexColor, white, black, Color
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
    from reportlab.platypus.flowables import HRFlowable

    rpt = generate_report_data(project)
    st = rpt['stats']; sched = rpt.get('schedule'); sett = rpt.get('settings', {})
    fc_data = rpt.get('forecast', {}) or {}
    fc_diams = fc_data.get('diameters', {}) if fc_data else {}
    phases = rpt.get('phase_order', ['fab'])
    phase_colors = ['#4472C4', '#ED7D31', '#8E44AD', '#27AE60']
    today = date.today()

    # Settings
    std_weeks = int(sett.get('standard_weeks', '9'))
    wks_saved = int(sett.get('committed_weeks_saved', '0'))
    days_saved_val = int(sett.get('committed_days_saved', '0'))
    total_saved = wks_saved * 7 + days_saved_val
    has_expediting = total_saved > 0
    transit_days = int(sett.get('sea_transit_days', '45'))

    # Colors
    BLUE = HexColor('#2F5496')
    DARK = HexColor('#404040')
    LIGHT_BLUE = HexColor('#D9E2F3')
    LIGHT_GREEN = HexColor('#E2EFDA')
    LIGHT_GRAY = HexColor('#F2F2F2')
    GREEN = HexColor('#27AE60')
    RED = HexColor('#E74C3C')
    ORANGE = HexColor('#F39C12')
    NAVY = HexColor('#002060')
    WHITE = white
    BLACK = black

    # Styles
    styles = getSampleStyleSheet()
    s_title = ParagraphStyle('RPT_Title', parent=styles['Title'], fontSize=18, textColor=BLUE, spaceAfter=2, alignment=TA_LEFT)
    s_heading = ParagraphStyle('RPT_H2', parent=styles['Heading2'], fontSize=13, textColor=BLUE, spaceBefore=6, spaceAfter=4, alignment=TA_LEFT)
    s_normal = ParagraphStyle('RPT_Normal', parent=styles['Normal'], fontSize=9, textColor=BLACK, leading=12)
    s_small = ParagraphStyle('RPT_Small', parent=styles['Normal'], fontSize=8, textColor=HexColor('#888888'), leading=10)
    s_center = ParagraphStyle('RPT_Center', parent=styles['Normal'], fontSize=9, textColor=BLACK, alignment=TA_CENTER, leading=11)
    s_center_bold = ParagraphStyle('RPT_CenterBold', parent=styles['Normal'], fontSize=9, textColor=BLACK, alignment=TA_CENTER, leading=11, fontName='Helvetica-Bold')
    s_cell = ParagraphStyle('RPT_Cell', parent=styles['Normal'], fontSize=8, textColor=BLACK, leading=10, alignment=TA_CENTER)
    s_cell_left = ParagraphStyle('RPT_CellL', parent=styles['Normal'], fontSize=8, textColor=BLACK, leading=10, alignment=TA_LEFT)
    s_cell_bold = ParagraphStyle('RPT_CellB', parent=styles['Normal'], fontSize=8, textColor=BLACK, leading=10, alignment=TA_CENTER, fontName='Helvetica-Bold')

    def p(text, style=s_normal):
        return Paragraph(str(text), style)

    def color_for_status(status):
        return {'on_time': GREEN, 'at_risk': ORANGE, 'delayed': RED}.get(status, HexColor('#95A5A6'))

    def status_label(status):
        return {'on_time': 'ON TIME', 'at_risk': 'AT RISK', 'delayed': 'DELAYED', 'not_started': 'NOT STARTED'}.get(status, status)

    page_w, page_h = landscape(A4)
    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    doc = SimpleDocTemplate(tmp.name, pagesize=landscape(A4),
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=12*mm, bottomMargin=12*mm)
    story = []

    # ── 1. Title Section ─────────────────────────────────────────────────────
    story.append(p('ENERXON \u2014 Production Report', s_title))
    story.append(Spacer(1, 2*mm))
    story.append(p(f'<b>Project:</b> {project} &nbsp;&nbsp;&nbsp; <b>Date:</b> {rpt["date"]}', s_normal))
    story.append(Spacer(1, 3*mm))
    s_big_pct = ParagraphStyle('RPT_BigPct', parent=styles['Normal'], fontSize=18, textColor=BLUE, fontName='Helvetica-Bold', leading=22)
    story.append(p(f'{st["overall_pct"]}% <font size="10" color="#888888">Overall Progress</font>', s_big_pct))
    story.append(Spacer(1, 2*mm))
    story.append(p(f'Total: {st["total"]} spools &nbsp;|&nbsp; Done: {st["completed"]} &nbsp;|&nbsp; In Progress: {st["in_progress"]} &nbsp;|&nbsp; Pending: {st["not_started"]}', s_small))
    story.append(Spacer(1, 8*mm))

    # ── 2. Schedule Status Table ─────────────────────────────────────────────
    if sched and sched.get('diameters'):
        story.append(p('SCHEDULE STATUS BY DIAMETER', s_heading))
        # Build headers dynamically
        phase_hdrs = [f'{ph.capitalize()} %' for ph in phases]
        headers = ['Diameter', 'Spools'] + phase_hdrs + ['Overall %', 'Diff', 'Status', 'Start', 'End', 'Forecast End']
        hdr_row = [p(f'<font color="white"><b>{h}</b></font>', s_cell) for h in headers]
        data_rows = [hdr_row]
        for d in sched['diameters']:
            dk = d['diameter']; fcd = fc_diams.get(dk, {})
            row_data = [p(f'<b>{dk}</b>', s_cell_left), p(str(d['spool_count']), s_cell)]
            for ph in phases:
                ph_val = (d.get('phase_avgs') or {}).get(ph, 0)
                row_data.append(p(f'<b>{ph_val}%</b>', s_cell_bold))
            row_data.append(p(f'<b>{d["actual_pct"]}%</b>', s_cell_bold))
            diff_val = d['diff']
            diff_str = f'+{diff_val}d' if diff_val > 0 else f'{diff_val}d' if diff_val < 0 else '0d'
            diff_color = '#27AE60' if diff_val > 0 else '#E74C3C' if diff_val < 0 else '#333333'
            row_data.append(p(f'<font color="{diff_color}">{diff_str}</font>', s_cell))
            s_color = {'on_time': '#27AE60', 'at_risk': '#F39C12', 'delayed': '#E74C3C'}.get(d['status'], '#95A5A6')
            row_data.append(p(f'<font color="{s_color}"><b>{status_label(d["status"])}</b></font>', s_cell))
            # Date columns — total start/end
            row_data.append(p(d.get('total_start', ''), s_cell))
            row_data.append(p(d.get('total_end', ''), s_cell))
            row_data.append(p(fcd.get('forecast_end', ''), s_cell))
            data_rows.append(row_data)

        num_cols = len(headers)
        avail_w = page_w - 30*mm
        # Proportional column widths
        base_widths = [42, 30] + [35]*len(phases) + [38, 32, 50, 48, 48, 48]
        total_base = sum(base_widths)
        col_widths = [w / total_base * avail_w for w in base_widths]

        t = Table(data_rows, colWidths=col_widths, repeatRows=1)
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#C0C0C0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, HexColor('#FAFBFD')]),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]
        # Highlight phase % cells >= 100 green
        phase_col_start = 2
        for ri, d in enumerate(sched['diameters'], 1):
            for pi, ph in enumerate(phases):
                ph_val = (d.get('phase_avgs') or {}).get(ph, 0)
                if ph_val >= 100:
                    t_style.append(('BACKGROUND', (phase_col_start+pi, ri), (phase_col_start+pi, ri), HexColor('#C6EFCE')))
            # Status cell color
            status_col = 2 + len(phases) + 2  # after phases, overall, diff
            s_bg = {'on_time': '#C6EFCE', 'at_risk': '#FCE4D6', 'delayed': '#FFC7CE'}.get(d['status'])
            if s_bg:
                t_style.append(('BACKGROUND', (status_col, ri), (status_col, ri), HexColor(s_bg)))
        t.setStyle(TableStyle(t_style))
        story.append(t)
        story.append(Spacer(1, 6*mm))

        # ── 3. Expediting Commitment Panel ───────────────────────────────────
        prod_start = None
        starts = [d['total_start'] for d in sched['diameters'] if d.get('total_start')]
        if starts:
            prod_start = date.fromisoformat(min(starts))
        if prod_start and has_expediting:
            std_end = prod_start + timedelta(days=std_weeks * 7 - 1)
            commit_end = std_end - timedelta(days=total_saved)
            fc_overall_end = fc_data.get('overall_forecast_end')
            fc_end_d = date.fromisoformat(fc_overall_end) if fc_overall_end else None
            fc_diff_commit = (commit_end - fc_end_d).days if fc_end_d else 0

            s_exp_card = ParagraphStyle('RPT_ExpCard', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, leading=20)
            exp_row = [
                p(f'<font color="#2F5496" size="14"><b>{prod_start.strftime("%d %b")}</b></font><br/><font size="8" color="#333333"><b>START</b></font>', s_exp_card),
                p(f'<font color="#888888" size="14"><s>{std_end.strftime("%d %b")}</s></font><br/><font size="8" color="#333333"><b>STANDARD END</b></font>', s_exp_card),
                p(f'<font color="#4472C4" size="14"><b>{commit_end.strftime("%d %b")}</b></font><br/><font size="8" color="#333333"><b>COMMITTED END</b></font>', s_exp_card),
                p(f'<font color="#4472C4" size="16"><b>{total_saved}d</b></font><br/><font size="8" color="#333333"><b>SAVED ({wks_saved} WK)</b></font>', s_exp_card),
                p(f'<font color="{"#27AE60" if fc_diff_commit >= 0 else "#E74C3C"}" size="14"><b>{fc_end_d.strftime("%d %b") if fc_end_d else chr(8212)}</b></font><br/><font size="8" color="#333333"><b>FORECAST {"&#10003;" if fc_diff_commit >= 0 else "&#10007;"}</b></font>', s_exp_card),
            ]
            exp_w = avail_w / 5
            exp_t = Table([exp_row], colWidths=[exp_w]*5)
            exp_t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), LIGHT_BLUE),
                ('GRID', (0,0), (-1,-1), 0.3, HexColor('#C0D4E8')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(KeepTogether([p('EXPEDITING COMMITMENT', s_heading), exp_t]))
            story.append(Spacer(1, 6*mm))
        elif prod_start:
            std_end = prod_start + timedelta(days=std_weeks * 7 - 1)
            commit_end = std_end; fc_end_d = None
        else:
            std_end = None; commit_end = None; fc_end_d = None; prod_start = None

        # ── 4. Production Gantt ──────────────────────────────────────────────
        gantt_elems = [p('PRODUCTION GANTT', s_heading)]  # Will be wrapped in KeepTogether
        if prod_start:
            fc_overall_end = fc_data.get('overall_forecast_end')
            if not fc_end_d and fc_overall_end:
                fc_end_d = date.fromisoformat(fc_overall_end)
            if has_expediting:
                num_weeks = std_weeks
            else:
                max_d = std_end or prod_start + timedelta(days=62)
                if fc_end_d and fc_end_d > max_d:
                    max_d = fc_end_d
                num_weeks = max(std_weeks, ((max_d - prod_start).days // 7) + 2)

            weeks = []
            for i in range(num_weeks):
                ws_date = prod_start + timedelta(days=i * 7)
                we_date = ws_date + timedelta(days=6)
                weeks.append((ws_date, we_date))

            ratio = (std_weeks - wks_saved) / std_weeks if has_expediting else 1.0

            # Build Gantt table
            gantt_hdrs = ['Diameter', 'Phase'] + [f'W{i+1}\n{ws.strftime("%d/%m")}-{we.strftime("%d/%m")}' for i, (ws, we) in enumerate(weeks)]
            gantt_data = []
            # Header row
            hdr = [p(f'<font color="white"><b>{h}</b></font>', s_cell) for h in gantt_hdrs]
            gantt_data.append(hdr)

            # Determine today column
            today_week_idx = None
            for i, (ws_d, we_d) in enumerate(weeks):
                if ws_d <= today <= we_d:
                    today_week_idx = i
                    break

            for dm_idx, d in enumerate(sched['diameters']):
                dk = d['diameter']; fcd = fc_diams.get(dk, {})
                overall_pct = fcd.get('overall_pct', 0) or 0
                dm_started = fcd.get('started', False)
                dm_fc_end_str = fcd.get('forecast_end', '')
                dm_fc_end = date.fromisoformat(dm_fc_end_str) if dm_fc_end_str else None
                dm_phase_avgs = fcd.get('phase_avgs', {}) or d.get('phase_avgs', {}) or {}

                # Parse schedule dates from phase_dates
                phase_dates = {}
                d_phase_dates = d.get('phase_dates', {})
                for ph in phases:
                    pd = d_phase_dates.get(ph, {})
                    if pd.get('start') and pd.get('end'):
                        phase_dates[ph] = (date.fromisoformat(pd['start']), date.fromisoformat(pd['end']))

                # Compute expedited dates per phase
                exp_phase_dates = {}
                prev_exp_end = None
                for pi, ph in enumerate(phases):
                    if ph not in phase_dates:
                        continue
                    ph_ps, ph_pe = phase_dates[ph]
                    if has_expediting and commit_end:
                        exp_s = prod_start + timedelta(days=int((ph_ps - prod_start).days * ratio))
                        exp_e = prod_start + timedelta(days=int((ph_pe - prod_start).days * ratio))
                        if exp_e > commit_end:
                            exp_e = commit_end
                        if prev_exp_end and exp_s < prev_exp_end:
                            exp_s = prev_exp_end
                        if exp_e < exp_s:
                            exp_e = exp_s
                    else:
                        exp_s = ph_ps; exp_e = ph_pe
                    exp_phase_dates[ph] = (exp_s, exp_e)
                    prev_exp_end = exp_e

                # One row per phase
                for pi, ph in enumerate(phases):
                    ph_pct = dm_phase_avgs.get(ph, 0) or 0
                    ph_hex = phase_colors[pi % len(phase_colors)]
                    is_first = pi == 0
                    is_last_phase = pi == len(phases) - 1
                    row = []
                    # Diameter label only on first phase row
                    if is_first:
                        row.append(p(f'<b>{dk}</b><br/><font size="6" color="#888888">{d["spool_count"]} spools</font>', s_cell_left))
                    else:
                        row.append(p('', s_cell))
                    # Phase label
                    row.append(p(f'<font color="#666666">{ph.capitalize()}</font>', s_cell))
                    # Week cells
                    for wi, (ws_d, we_d) in enumerate(weeks):
                        cell_text = ''
                        cell_bg = None
                        if ph in phase_dates and ph in exp_phase_dates:
                            ph_ps, ph_pe = phase_dates[ph]
                            exp_s, exp_e = exp_phase_dates[ph]
                            in_std = ph_ps <= we_d and ph_pe >= ws_d
                            in_exp = exp_s <= we_d and exp_e >= ws_d
                            is_saved_cell = has_expediting and in_std and not in_exp
                            is_forecast = is_last_phase and dm_started and dm_fc_end and overall_pct < 100 and dm_fc_end >= ws_d and dm_fc_end <= we_d

                            if in_exp:
                                cell_bg = HexColor(ph_hex)
                                if ph_pct >= 100 and we_d < today:
                                    cell_text = '\u2713'
                                elif today_week_idx is not None and wi == today_week_idx and 0 < ph_pct < 100:
                                    cell_text = f'{ph_pct:.0f}%'
                            elif is_saved_cell:
                                cell_bg = LIGHT_GREEN
                            if is_forecast:
                                if not in_exp: cell_bg = None  # transparent
                                cell_text = '\u25c6'
                        # Text color: white on colored bg, green for forecast, dark otherwise
                        if cell_text:
                            if cell_text == '\u25c6':
                                txt_color = '#1B7340'
                            elif cell_bg and cell_bg != LIGHT_GREEN:
                                txt_color = 'white'
                            else:
                                txt_color = '#333'
                            row.append(p(f'<font color="{txt_color}" size="7"><b>{cell_text}</b></font>', s_cell))
                        else:
                            row.append(p('', s_cell))
                        # Store bg info for styling later
                        if '_gantt_bgs' not in d:
                            d['_gantt_bgs'] = {}
                        d['_gantt_bgs'][(pi, wi)] = cell_bg
                    gantt_data.append(row)

            # Column widths for Gantt
            diam_col_w = 55
            phase_col_w = 32
            week_col_w = max(14, (avail_w - diam_col_w - phase_col_w) / max(num_weeks, 1))
            gantt_col_widths = [diam_col_w, phase_col_w] + [week_col_w] * num_weeks

            gantt_t = Table(gantt_data, colWidths=gantt_col_widths, repeatRows=1)
            gantt_style = [
                ('BACKGROUND', (0,0), (-1,0), DARK),
                ('TEXTCOLOR', (0,0), (-1,0), WHITE),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.3, HexColor('#E0E0E0')),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ]
            # Today column highlight
            if today_week_idx is not None:
                tc = today_week_idx + 2  # offset for Diameter+Phase columns
                gantt_style.append(('BACKGROUND', (tc, 0), (tc, 0), HexColor('#C00000')))
                # Red borders on today column for all data rows
                for ri in range(1, len(gantt_data)):
                    gantt_style.append(('LINEAFTER', (tc, ri), (tc, ri), 1.5, RED))
                    gantt_style.append(('LINEBEFORE', (tc, ri), (tc, ri), 1.5, RED))

            # Apply phase bar backgrounds
            data_row_idx = 1
            for dm_idx, d in enumerate(sched['diameters']):
                for pi, ph in enumerate(phases):
                    for wi in range(num_weeks):
                        bg = d.get('_gantt_bgs', {}).get((pi, wi))
                        if bg:
                            gantt_style.append(('BACKGROUND', (wi+2, data_row_idx), (wi+2, data_row_idx), bg))
                    data_row_idx += 1
                # Merge diameter cells across phase rows
                if len(phases) > 1:
                    first_row = data_row_idx - len(phases)
                    gantt_style.append(('SPAN', (0, first_row), (0, first_row + len(phases) - 1)))

            gantt_t.setStyle(TableStyle(gantt_style))
            # Clean up temp _gantt_bgs
            for d in sched['diameters']:
                d.pop('_gantt_bgs', None)

            gantt_elems.append(gantt_t)

            # Legend
            legend_items = []
            for pi, ph in enumerate(phases):
                legend_items.append(f'<font color="{phase_colors[pi % len(phase_colors)]}">\u25a0</font> {ph.capitalize()}')
            if has_expediting:
                legend_items.append('<font color="#A9D18E">\u25a0</font> Saved')
            legend_items.append('<font color="#1B7340">\u25c6</font> Forecast')
            legend_items.append('<font color="#E74C3C">|</font> Today')
            gantt_elems.append(p('&nbsp;&nbsp;&nbsp;'.join(legend_items), s_small))
            story.append(KeepTogether(gantt_elems))
            story.append(Spacer(1, 6*mm))

        # ── 5. Production Rate ───────────────────────────────────────────────
        actual_weld = fc_data.get('actual_weld_ipd', 0) or 0
        actual_paint = fc_data.get('actual_paint_m2d', 0) or 0
        weld_cap = fc_data.get('welding_capability', 0) or 0
        paint_cap = fc_data.get('painting_capability', 0) or 0
        steps_def = get_project_steps(project)
        has_surface = any(s.get('hours_variable') == 'surface' for s in steps_def)

        rate_elems = [p('PRODUCTION RATE', s_heading)]
        rate_data = []
        weld_color = '#27AE60' if actual_weld >= weld_cap else '#E74C3C'
        weld_pct = min(actual_weld / max(weld_cap, 1) * 100, 100) if weld_cap else 0
        rate_data.append([
            p('<b>Welding</b>', s_cell_left),
            p(f'<font color="{weld_color}" size="12"><b>{actual_weld}</b></font>', s_cell),
            p(f'/ {weld_cap}', s_cell),
            p('linear inches/day', s_cell),
            p(f'<font color="{weld_color}">{weld_pct:.0f}% of target</font>', s_cell),
        ])
        if has_surface:
            surface_label = phases[-1].capitalize() if len(phases) > 1 else 'Surface'
            paint_color = '#27AE60' if actual_paint >= paint_cap else '#E74C3C'
            paint_pct = min(actual_paint / max(paint_cap, 1) * 100, 100) if paint_cap else 0
            rate_data.append([
                p(f'<b>{surface_label}</b>', s_cell_left),
                p(f'<font color="{paint_color}" size="12"><b>{actual_paint}</b></font>', s_cell),
                p(f'/ {paint_cap}', s_cell),
                p('m\u00b2/day', s_cell),
                p(f'<font color="{paint_color}">{paint_pct:.0f}% of target</font>', s_cell),
            ])
        rate_widths = [avail_w * f for f in [0.22, 0.15, 0.1, 0.2, 0.33]]
        rate_t = Table(rate_data, colWidths=rate_widths)
        rate_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#D0D0D0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        rate_elems.append(rate_t)
        story.append(KeepTogether(rate_elems))
        story.append(Spacer(1, 6*mm))

        # ── 6. Results Summary — Visual KPI cards ────────────────────────────
        if has_expediting and std_end and commit_end:
            if not fc_end_d and fc_data and fc_data.get('overall_forecast_end'):
                fc_end_d = date.fromisoformat(fc_data['overall_forecast_end'])
            fc_saved = (std_end - fc_end_d).days if fc_end_d else 0
            fc_diff_c = (commit_end - fc_end_d).days if fc_end_d else 0
            cards = [
                ('#2F5496', f'{st["overall_pct"]}%', 'PROGRESS', f'{st["total"]} spools | {st["completed"]} done'),
                ('#4472C4', f'{commit_end.strftime("%d %b %Y")}', 'COMMITTED END', f'{total_saved}d saved ({wks_saved} wk)'),
                ('#27AE60' if fc_diff_c >= 0 else '#E74C3C',
                 f'{fc_end_d.strftime("%d %b %Y") if fc_end_d else chr(8212)}',
                 'FORECAST END',
                 f'{"+" if fc_diff_c >= 0 else ""}{fc_diff_c}d vs commitment' if fc_end_d else ''),
                ('white', str(today) if st['completed'] >= st['total'] else chr(8212), 'ACTUAL END', 'Shown when complete'),
            ]
        else:
            fc_end_d_val = date.fromisoformat(fc_data.get('overall_forecast_end')) if fc_data and fc_data.get('overall_forecast_end') else None
            cards = [
                ('#2F5496', f'{st["overall_pct"]}%', 'PROGRESS', f'{st["total"]} spools | {st["completed"]} done'),
                ('#4472C4', fc_end_d_val.strftime('%d %b %Y') if fc_end_d_val else chr(8212), 'FORECAST END', 'Based on actual rate'),
                ('white', str(today) if st['completed'] >= st['total'] else chr(8212), 'ACTUAL END', 'Shown when complete'),
            ]
        # Build as a row of cards — big number on top, label below
        s_card = ParagraphStyle('RPT_Card', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, leading=20)
        card_row = []
        for ci, (color, val, label, sub) in enumerate(cards):
            is_dark = ci == len(cards) - 1  # last card = dark bg
            lbl_color = 'white' if is_dark else '#333333'
            sub_color = '#AAAAAA' if is_dark else '#888888'
            card_row.append(p(
                f'<font color="{color}" size="16"><b>{val}</b></font><br/>'
                f'<font color="{lbl_color}" size="8"><b>{label}</b></font><br/>'
                f'<font color="{sub_color}" size="7">{sub}</font>', s_card))
        card_w = avail_w / len(cards)
        card_t = Table([card_row], colWidths=[card_w]*len(cards))
        card_style = [
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (-2,-1), LIGHT_BLUE),
            ('BACKGROUND', (-1,0), (-1,-1), DARK),
            ('BOX', (0,0), (-1,-1), 0.5, HexColor('#C0D4E8')),
        ]
        for ci in range(len(cards)):
            card_style.append(('LINEBEFORE', (ci, 0), (ci, -1), 0.3, HexColor('#C0D4E8')))
        card_t.setStyle(TableStyle(card_style))
        story.append(KeepTogether([p('RESULTS SUMMARY', s_heading), card_t]))
        story.append(Spacer(1, 6*mm))

        # ── 7. Sea Transit ───────────────────────────────────────────────────
        if has_expediting and commit_end:
            if not fc_end_d and fc_data and fc_data.get('overall_forecast_end'):
                fc_end_d = date.fromisoformat(fc_data['overall_forecast_end'])
            commit_arrival = commit_end + timedelta(days=transit_days)
            fc_arrival = fc_end_d + timedelta(days=transit_days) if fc_end_d else None
            # Visual KPI cards for transit
            s_transit_card = ParagraphStyle('RPT_TransitCard', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, leading=20)
            transit_row = [
                p(f'<font color="white" size="16"><b>~{transit_days}d</b></font><br/><font size="8" color="#99BBDD"><b>SEA TRANSIT</b></font>', s_transit_card),
                p(f'<font color="white" size="14"><b>{commit_arrival.strftime("%d %b %Y")}</b></font><br/><font size="8" color="#99BBDD"><b>COMMITTED ARRIVAL</b></font>', s_transit_card),
                p(f'<font color="white" size="14"><b>{fc_arrival.strftime("%d %b %Y") if fc_arrival else chr(8212)}</b></font><br/><font size="8" color="#99BBDD"><b>FORECAST ARRIVAL</b></font>', s_transit_card),
            ]
            transit_t = Table([transit_row], colWidths=[avail_w/3]*3)
            transit_t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), NAVY),
                ('VALIGN', (0,0), (-1,0), 'BOTTOM'), ('VALIGN', (0,1), (-1,1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 0),
                ('TOPPADDING', (0,1), (-1,1), 0), ('BOTTOMPADDING', (0,1), (-1,1), 6),
                ('BOX', (0,0), (-1,-1), 0.5, HexColor('#003366')),
            ]))
            story.append(KeepTogether([p('SEA TRANSIT', s_heading), transit_t]))

    doc.build(story)
    return send_file(tmp.name, as_attachment=True, download_name=f"{project}_report_{today.strftime('%Y%m%d')}.pdf",
                     mimetype='application/pdf')

# ── HTML Templates ───────────────────────────────────────────────────────────
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
<div class="header"><div style="display:flex;align-items:center;gap:12px"><div><h1 style="margin:0">Production Tracker</h1><div class="sub" style="margin:0">\u751f\u4ea7\u8fdb\u5ea6\u8ffd\u8e2a\u7cfb\u7edf \u2014 Select a project / \u9009\u62e9\u9879\u76ee</div></div></div></div>
<div class="proj-list" id="projects"><div class="empty">Loading projects... / \u52a0\u8f7d\u4e2d...</div></div>
<script>
async function load(){
  const r = await fetch('/api/projects'); const projects = await r.json();
  if(!projects.length){ document.getElementById('projects').innerHTML='<div class="empty">No projects yet / \u6682\u65e0\u9879\u76ee<br><br>Use the API to import spools:<br><code>POST /api/import</code></div>'; return; }
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

# PROJECT_HTML, SPOOL_HTML, REPORT_HTML — preserved from original with dynamic hold/release
# These templates are loaded from the API which now returns is_hold_point/is_release flags

PROJECT_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ project }} — Tracker</title><style>""" + COMMON_CSS + """
.section{padding:0 16px 16px}.section h2{font-size:16px;color:#2F5496;margin:16px 0 8px}
.toolbar{display:flex;gap:8px;padding:8px 16px;flex-wrap:wrap}
.diam-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px;padding:0 16px}
.diam-card{background:#fff;border-radius:10px;padding:14px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08);position:relative;border-top:3px solid #e8e8e8}
.diam-card .d{font-size:22px;font-weight:700;color:#2F5496}.diam-card .p{font-size:11px;color:#888}
.d-ahead{border-top-color:#27ae60}.d-ontrack{border-top-color:#4472C4}.d-atrisk{border-top-color:#f39c12}.d-behind{border-top-color:#e74c3c}.d-pending{border-top-color:#e8e8e8}
.pace-badge{position:absolute;top:6px;right:6px;font-size:7px;font-weight:700;padding:1px 5px;border-radius:4px;text-transform:uppercase;letter-spacing:.3px}
.pb-ahead{background:#e8f5e9;color:#27ae60}.pb-ontrack{background:#e3f2fd;color:#4472C4}.pb-atrisk{background:#fff3e0;color:#f39c12}.pb-behind{background:#fce4ec;color:#e74c3c}.pb-pending{background:#f5f5f5;color:#bbb}
.spool-row{display:flex;align-items:center;gap:10px;padding:10px 16px;background:#fff;margin:4px 16px;border-radius:8px;cursor:pointer;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.spool-row:hover{background:#f8f9fb}.spool-row .info{flex:1}.spool-row .name{font-weight:600;font-size:14px;color:#2F5496}
.spool-row .meta{font-size:11px;color:#888}.spool-row .bar{width:80px}.spool-row .pct{font-size:14px;font-weight:700;min-width:45px;text-align:right}
.activity-item{padding:8px 0;border-bottom:1px solid #f0f2f5;font-size:12px}
.filter-row{display:flex;gap:8px;padding:8px 16px;flex-wrap:wrap}
.filter-row select,.filter-row input{padding:6px 10px;border:1px solid #ddd;border-radius:6px;font-size:12px}
.target-banner{display:flex;align-items:center;gap:14px;padding:10px 18px;margin:8px 16px;border-radius:10px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.08);flex-wrap:wrap;border-left:4px solid #2F5496}
.tb-section{text-align:center;padding:0 12px;border-right:1px solid #eee;min-width:80px}.tb-section:last-child{border-right:none}
.tb-label{font-size:8px;color:#888;text-transform:uppercase;letter-spacing:.3px}.tb-value{font-size:18px;font-weight:700}.tb-sub{font-size:8px;color:#aaa}
.status-pill{display:inline-block;padding:4px 10px;border-radius:12px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.sp-green{background:#e8f5e9;color:#27ae60}.sp-red{background:#fce4ec;color:#e74c3c}
.rate-strip{display:flex;align-items:center;gap:14px;padding:10px 18px;margin:0 16px 8px;border-radius:10px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.08);flex-wrap:wrap;border-left:4px solid #4472C4}
.rs-title{font-size:11px;font-weight:700;color:#2F5496;white-space:nowrap}
.rs-item{display:flex;align-items:center;gap:6px;padding:0 10px;border-right:1px solid #eee}.rs-item:last-of-type{border-right:none}
.rs-lbl{font-size:8px;color:#888;text-transform:uppercase}.rs-val{font-size:20px;font-weight:700}
.rs-badge{padding:3px 10px;border-radius:8px;font-size:9px;font-weight:700;margin-left:auto;white-space:nowrap}
.rs-good{background:#e8f5e9;color:#27ae60}.rs-bad{background:#fce4ec;color:#e74c3c}
</style></head><body>
<div class="header">
  <div style="display:flex;align-items:center;gap:12px">
    <a class="back" href="/">\u2190 Home</a>
    <div style="flex:1"><h1>{{ project }}</h1><div class="sub" id="subtitle">Loading... / \u52a0\u8f7d\u4e2d...</div></div>
  </div>
</div>
<div class="toolbar">
  <a class="btn" href="/api/project/{{ project }}/export">\U0001f4e5 Export Excel</a>
  <a class="btn" href="/project/{{ project }}/report" style="background:#27ae60">\U0001f4ca Report / \u62a5\u544a</a>
  <a class="btn" href="/api/project/{{ project }}/report/download" style="background:#ED7D31">\U0001f4ca Report Excel</a>
  <a class="btn" href="/api/project/{{ project }}/report/pdf" style="background:#E74C3C">\U0001f4c4 Report PDF</a>
</div>
<div id="target-banner"></div>
<div id="rate-strip"></div>
<div class="stats-grid" id="stats"></div>
<div id="diam" class="diam-grid"></div>
<div class="filter-row">
  <input id="q" placeholder="Search spool / \u641c\u7d22..." oninput="filter()">
  <select id="fd" onchange="filter()"><option value="">All Diameters</option></select>
  <select id="fl" onchange="filter()"><option value="">All Lines</option><option value="A">A</option><option value="B">B</option><option value="C">C</option></select>
  <select id="fs" onchange="filter()"><option value="">All Status</option><option value="done">Done / \u5b8c\u6210</option><option value="wip">WIP / \u8fdb\u884c\u4e2d</option><option value="todo">Pending / \u5f85\u5f00\u59cb</option></select>
</div>
<div id="list"></div>
<div id="act" class="section"></div>
<script>
const P='{{project}}';
let all=[];
async function load(){
  const [dr, sr] = await Promise.all([fetch(`/api/project/${P}/dashboard`), fetch(`/api/project/${P}/spools`)]);
  const st = await dr.json(); all = await sr.json();
  const fc = st.forecast||{}, sett = st.settings||{}, schd = st.schedule_data, pr = st.production_rate||{};
  const phases = st.phase_order || schd?.phase_order || ['fab'];
  const phaseColors = ['#4472C4', '#ED7D31', '#8E44AD', '#27AE60'];
  const toLocal = s => {const [y,m,d]=s.split('-');return new Date(+y,+m-1,+d);};
  const addDays = (dt,n) => new Date(dt.getFullYear(),dt.getMonth(),dt.getDate()+n);
  const fmt = d => d.toLocaleDateString('en',{day:'2-digit',month:'short'});
  document.getElementById('subtitle').textContent=`${st.total} spools \u00b7 ${st.overall_pct}% \u00b7 ${st.completed} done / \u5b8c\u6210 ${st.completed}`;
  document.getElementById('stats').innerHTML=[
    {v:st.total,l:'Total / \u603b\u6570'},{v:st.completed,l:'Done / \u5b8c\u6210',c:'#27ae60'},
    {v:st.in_progress,l:'WIP / \u8fdb\u884c\u4e2d',c:'#f39c12'},{v:st.not_started,l:'Pending / \u5f85\u5f00\u59cb',c:'#e74c3c'},
    {v:st.past_rt||0,l:'Past RT / \u8fc7RT',c:'#4472C4'}
  ].map(x=>`<div class="stat-card"><div class="value" style="color:${x.c||'#2F5496'}">${x.v}</div><div class="label">${x.l}</div></div>`).join('');

  // Expediting banner
  const stdWeeks = parseInt(sett.standard_weeks||'9');
  const wksSaved = parseInt(sett.committed_weeks_saved||'0');
  const daysSaved = parseInt(sett.committed_days_saved||'0');
  const totalSaved = wksSaved*7+daysSaved;
  const hasExpediting = totalSaved > 0;
  if(hasExpediting && schd && schd.diameters && schd.diameters.length){
    const starts = schd.diameters.map(x=>x.total_start).filter(x=>x).sort();
    if(starts.length){
      const psDate = toLocal(starts[0]);
      const stdEnd = addDays(psDate, stdWeeks*7 - 1);
      const commitEnd = addDays(stdEnd, -totalSaved);
      const fcEnd = fc.overall_forecast_end ? toLocal(fc.overall_forecast_end) : null;
      const today = new Date(); today.setHours(0,0,0,0);
      const daysToTarget = Math.round((commitEnd - today) / 86400000);
      const fcSaved = fcEnd ? Math.ceil((stdEnd - fcEnd) / 86400000) : 0;
      const fcDiff = fcEnd ? Math.ceil((commitEnd - fcEnd) / 86400000) : 0;
      const statusCls = fcDiff >= 0 ? 'tb-ok' : 'tb-warn';
      const pillCls = fcDiff >= 0 ? 'sp-green' : 'sp-red';
      const pillText = fcDiff >= 0 ? `\u2713 ${fcDiff}d ahead / \u8d85\u524d` : `\u2717 ${Math.abs(fcDiff)}d behind / \u843d\u540e`;
      document.getElementById('target-banner').innerHTML=`<div class="target-banner ${statusCls}">
        <div class="tb-section"><div class="tb-label">Expediting Target / \u52a0\u6025\u76ee\u6807</div><div class="tb-value" style="color:#4472C4">${fmt(commitEnd)}</div><div class="tb-sub">Committed / \u627f\u8bfa\u5b8c\u5de5</div></div>
        <div class="tb-section"><div class="tb-label">Forecast End / \u9884\u6d4b\u5b8c\u5de5</div><div class="tb-value" style="color:#27ae60">${fmt(fcEnd||new Date())}</div><div class="tb-sub">Based on rate / \u57fa\u4e8e\u8fdb\u5ea6</div></div>
        <div class="tb-section"><div class="tb-label">Days to Target / \u8ddd\u76ee\u6807</div><div class="tb-value" style="color:#2F5496">${daysToTarget}</div><div class="tb-sub">days left / \u5269\u4f59\u5929\u6570</div></div>
        <div class="tb-section"><div class="tb-label">Expediting Saved / \u52a0\u6025\u8282\u7701</div><div class="tb-value" style="color:#4472C4">${totalSaved}<span style="font-size:10px;font-weight:400"> days</span></div><div class="tb-sub">vs standard / \u8f83\u6807\u51c6</div></div>
        <div class="tb-section"><div class="tb-label">Forecast Saved / \u9884\u6d4b\u8282\u7701</div><div class="tb-value" style="color:#27ae60">${fcSaved}<span style="font-size:10px;font-weight:400"> days</span></div><div class="tb-sub">predicted / \u9884\u6d4b</div></div>
        <div class="tb-section" style="border-right:none;margin-left:auto"><div class="status-pill ${pillCls}">${pillText}</div><div style="font-size:8px;color:#888;margin-top:2px">vs commitment / \u8f83\u627f\u8bfa</div></div>
      </div>`;
      // Daily rate + bottleneck
      const avgRate = pr.avg_7day || 0;
      const trend = pr.trend || 0;
      const todaySteps = pr.today_steps || 0;
      const remaining = st.total - st.completed;
      const targetRate = daysToTarget > 0 ? (remaining / daysToTarget).toFixed(1) : '\u2014';
      const aboveTarget = avgRate >= parseFloat(targetRate);
      const trendArrow = trend >= 0 ? `<span style="color:#27ae60;font-size:10px;font-weight:600">\u25b2${trend}</span>` : `<span style="color:#e74c3c;font-size:10px;font-weight:600">\u25bc${Math.abs(trend)}</span>`;
      let bottleneck = null;
      if(schd && schd.diameters){
        let worstRatio = 999;
        schd.diameters.forEach(dm => {
          if(dm.actual_pct >= 100 || dm.status === 'not_started') return;
          const ratio = dm.actual_pct / Math.max(dm.expected_pct, 1);
          if(ratio < worstRatio){ worstRatio = ratio; bottleneck = dm; }
        });
      }
      let bnHtml = '';
      if(bottleneck && bottleneck.actual_pct < 100){
        const fcDiam = fc.diameters ? fc.diameters[bottleneck.diameter] : null;
        const fcEndDiam = fcDiam ? fcDiam.forecast_end : '\u2014';
        const neededRate = daysToTarget > 0 ? ((100 - bottleneck.actual_pct) / 100 * bottleneck.spool_count / daysToTarget).toFixed(1) : '\u2014';
        bnHtml = `<div style="background:#fff;border-radius:8px;padding:10px 16px;box-shadow:0 1px 2px rgba(0,0,0,.05);min-width:240px;border-left:4px solid #e74c3c;display:flex;flex-direction:column;justify-content:center">
          <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:.3px">Critical Path / \u5173\u952e\u8def\u5f84</div>
          <div style="display:flex;align-items:baseline;gap:5px;margin:2px 0"><span style="font-size:20px;font-weight:700;color:#e74c3c">${bottleneck.diameter}</span><span style="font-size:11px;color:#888">${bottleneck.spool_count} spools \u00b7 slowest / \u6700\u6162</span></div>
          <div style="font-size:10px;color:#666">Need / \u9700\u8981 <strong>${neededRate} spools/day / \u6bcf\u65e5</strong> to hit target / \u8fbe\u5230\u76ee\u6807</div>
          <div style="font-size:9px;color:#999;margin-top:2px">${bottleneck.actual_pct}% done \u00b7 Forecast / \u9884\u6d4b: ${fcEndDiam}</div>
        </div>`;
      }
      document.getElementById('rate-strip').innerHTML = `<div style="display:flex;gap:10px;margin:0 16px 8px;flex-wrap:wrap">
        <div class="rate-strip" style="flex:1;min-width:400px;margin:0">
          <div class="rs-title">\U0001f4ca Daily Rate / \u6bcf\u65e5\u751f\u4ea7\u7387</div>
          <div class="rs-item"><div><div class="rs-lbl">Target / \u76ee\u6807</div><div class="rs-val" style="color:#2F5496">${targetRate}</div></div><div class="rs-lbl">spools/day<br>\u6bcf\u65e5\u9700\u5b8c\u6210</div></div>
          <div class="rs-item"><div><div class="rs-lbl">7-day avg / 7\u5929\u5747\u503c</div><div style="display:flex;align-items:baseline;gap:3px"><div class="rs-val" style="color:${aboveTarget?'#27ae60':'#e74c3c'}">${avgRate}</div>${trendArrow}</div></div><div class="rs-lbl">spools/day<br>\u8f83\u4e0a\u5468</div></div>
          <div class="rs-item" style="border-right:none"><div><div class="rs-lbl">Steps today / \u4eca\u65e5\u6b65\u9aa4</div><div class="rs-val" style="color:#4472C4">${todaySteps}</div></div><div class="rs-lbl">completed<br>\u4eca\u65e5\u5b8c\u6210</div></div>
          <div class="rs-badge ${aboveTarget?'rs-good':'rs-bad'}">${aboveTarget?'\u2713 Above target / \u8d85\u8fc7\u76ee\u6807':'\u26a0 Below target / \u4f4e\u4e8e\u76ee\u6807'}</div>
        </div>
        ${bnHtml}
      </div>`;
    }
  }

  // Diameter cards
  const ds=Object.entries(st.by_diameter).sort((a,b)=>(parseInt(b[0])||0)-(parseInt(a[0])||0));
  document.getElementById('diam').innerHTML=ds.map(([d,v])=>{
    let cls='d-pending',badge='PENDING / \u5f85\u5f00\u59cb',badgeCls='pb-pending',paceText='',barColor='#ccc';
    if(schd && schd.diameters){
      const dm = schd.diameters.find(x=>x.diameter===d);
      if(dm){
        const diff = dm.actual_pct - dm.expected_pct;
        if(dm.status==='not_started'){cls='d-pending';badge='PENDING / \u5f85\u5f00\u59cb';badgeCls='pb-pending';barColor='#ccc';}
        else if(diff >= 5){cls='d-ahead';badge='AHEAD / \u8d85\u524d';badgeCls='pb-ahead';barColor='#27ae60';paceText=`+${Math.round(diff)}% ahead / \u8d85\u524d`;}
        else if(diff >= -5){cls='d-ontrack';badge='ON TRACK / \u8fbe\u6807';badgeCls='pb-ontrack';barColor='#4472C4';paceText=`${diff>=0?'+':''}${Math.round(diff)}% on pace / \u8fbe\u6807`;}
        else if(diff >= -15){cls='d-atrisk';badge='AT RISK / \u6709\u98ce\u9669';badgeCls='pb-atrisk';barColor='#f39c12';paceText=`${Math.round(diff)}% behind / \u843d\u540e`;}
        else{cls='d-behind';badge='BEHIND / \u843d\u540e';badgeCls='pb-behind';barColor='#e74c3c';paceText=`${Math.round(diff)}% behind / \u843d\u540e`;}
        if(dm.expected_pct===0 && dm.actual_pct>0){cls='d-ahead';badge='AHEAD / \u8d85\u524d';badgeCls='pb-ahead';barColor='#27ae60';paceText='Started early / \u63d0\u524d\u5f00\u59cb';}
      } else if(v.avg_pct > 0){cls='d-ontrack';badge='WIP';badgeCls='pb-ontrack';barColor='#4472C4';}
    } else if(v.avg_pct > 0){cls='d-ontrack';barColor='#4472C4';}
    else if(v.avg_pct >= 100){cls='d-ahead';barColor='#27ae60';}
    const phAvgs = v.phase_avgs || {};
    const phaseBars = phases.map((ph,pi) => {
      const pv = phAvgs[ph]||0;
      return `<div style="margin-top:${pi===0?6:2}px"><div style="font-size:8px;color:#aaa">${ph.charAt(0).toUpperCase()+ph.slice(1)}</div><div class="pbar-bg" style="height:8px"><div class="pbar-fill" style="width:${pv}%;background:${phaseColors[pi%phaseColors.length]};height:100%"></div></div></div>`;
    }).join('');
    return `<div class="diam-card ${cls}"><div class="pace-badge ${badgeCls}">${badge}</div><div class="d">${d}</div><div class="p">${v.total} spools</div>
      ${phaseBars}
      <div style="font-size:12px;margin-top:4px;font-weight:600;color:${barColor}">${v.avg_pct}%</div>
      ${paceText?`<div style="font-size:9px;color:#888;margin-top:2px">${paceText}</div>`:''}</div>`;
  }).join('');
  render(all);
  const diamsSet = [...new Set(all.map(s=>s.spool.main_diameter||'?'))].sort((a,b)=>(parseInt(b)||0)-(parseInt(a)||0));
  const fdEl = document.getElementById('fd');
  const curFd = fdEl.value;
  fdEl.innerHTML = '<option value="">All Diameters</option>';
  diamsSet.forEach(d=>{ const o=document.createElement('option'); o.value=d; o.textContent=d; fdEl.appendChild(o); });
  fdEl.value = curFd;
  if(st.recent_activity&&st.recent_activity.length)
    document.getElementById('act').innerHTML='<h2 style="font-size:16px;color:#2F5496;margin:8px 0">Recent / \u6700\u8fd1\u52a8\u6001</h2>'+
      st.recent_activity.slice(0,10).map(a=>`<div class="activity-item"><strong>${a.spool_id}</strong> \u2014 ${a.details||a.action} <span style="color:#aaa;font-size:11px">${a.timestamp||''}</span></div>`).join('');
}
function render(sp){
  document.getElementById('list').innerHTML=sp.map(s=>{
    const p=s.progress_pct,c=p>=100?'pct-green':p>0?'pct-yellow':'pct-red',bg=p>=100?'#27ae60':p>0?'#f39c12':'#e8e8e8',l=s.spool.line||'?';
    return`<div class="spool-row" onclick="location.href='/project/${P}/spool/${s.spool.spool_id}'">
      <span class="line-badge line-${l}">${l}</span>
      <div class="info"><div class="name">${s.spool.spool_id}</div><div class="meta">${s.spool.main_diameter||''} \u00b7 ${s.spool.iso_no||''}</div></div>
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
  <a class="back" href="/project/{{ project }}">\u2190 {{ project }}</a>
  <h1>{{ spool_id }}</h1>
  <div class="sub" id="sub-info">Loading...</div>
</div>
<div class="info-bar" id="info-bar"></div>
<div style="padding:8px 16px;display:none" id="dwg-wrap">
  <a class="btn" id="dwg-btn" target="_blank" style="width:100%;text-align:center;display:block;padding:10px;font-size:14px">\U0001f4c4 View Drawing / \u67e5\u770b\u56fe\u7eb8</a>
</div>
<div class="prog"><div class="big" id="prog-pct">--</div><div class="lbl">Progress / \u8fdb\u5ea6</div>
  <div class="pbar-bg" style="max-width:300px;margin:8px auto"><div class="pbar-fill" id="prog-bar" style="width:0%;background:#2F5496"></div></div>
</div>
<div class="op-input"><input id="operator" placeholder="Operator name / \u64cd\u4f5c\u5458\u59d3\u540d" value=""></div>
<div class="checklist" id="steps"></div>
<script>
const P='{{project}}',S='{{spool_id}}';
let stepDefs=[], stepMap={};
async function load(){
  const r = await fetch(`/api/project/${P}/spool/${S}`);
  const d = await r.json();
  if(d.error){document.getElementById('steps').innerHTML=`<p style="color:red">${d.error}</p>`;return;}
  const sp=d.spool;
  stepDefs = d.step_definitions || [];
  document.getElementById('sub-info').textContent=`${sp.main_diameter||''} \u00b7 ${sp.iso_no||''} \u00b7 ${sp.marking||''}`;
  document.getElementById('info-bar').innerHTML=[
    ['Diameter / \u53e3\u5f84',sp.main_diameter],['ISO',sp.iso_no],['Line / \u7ebf',sp.line],['MK',sp.mk_number],['Marking / \u6807\u8bc6',sp.marking]
  ].filter(x=>x[1]).map(([l,v])=>`<div class="info-item"><span class="lb">${l}:</span> <span class="vl">${v}</span></div>`).join('');
  document.getElementById('prog-pct').textContent=d.progress_pct+'%';
  document.getElementById('prog-bar').style.width=d.progress_pct+'%';
  document.getElementById('prog-bar').style.background=d.progress_pct>=100?'#27ae60':d.progress_pct>0?'#2F5496':'#e8e8e8';
  stepMap={};
  (d.steps||[]).forEach(s=>stepMap[s.step_number]=s);
  // Build hold/release lookup from step_definitions
  const holdSteps = new Set(stepDefs.filter(s=>s.is_hold_point).map(s=>s.number));
  const releaseSteps = new Set(stepDefs.filter(s=>s.is_release).map(s=>s.number));
  document.getElementById('steps').innerHTML=stepDefs.map(sd=>{
    const st=stepMap[sd.number]||{completed:0};
    const done=st.completed;
    const badges=[];
    if(holdSteps.has(sd.number)) badges.push('<span class="wbadge" style="background:#EDE7F6;color:#5E35B1">\u2605 HOLD POINT</span>');
    if(releaseSteps.has(sd.number)) badges.push('<span class="wbadge" style="background:#E8F5E9;color:#2E7D32">\U0001f3c1 WITNESS</span>');
    return `<div class="step ${done?'done':'pending'}" id="step-${sd.number}">
      <div class="step-h" onclick="toggle(${sd.number})">
        <div class="num">${sd.number}</div>
        <div class="text"><div class="en">${sd.name_en} ${badges.join(' ')}</div><div class="cn">${sd.name_cn||''}</div></div>
        <div class="chk">${done?'\u2705':'\u2b1c'}</div>
      </div>
      ${done?`<div class="step-meta">By ${st.completed_by||'?'} \u00b7 ${(st.completed_at||'').substring(0,16)}</div>`:''}
      <div class="step-rem"><input placeholder="Remarks / \u5907\u6ce8" value="${st.remarks||''}" onchange="remark(${sd.number},this.value)"></div>
    </div>`;
  }).join('');
  // Drawing button
  try{
    const dr=await fetch(`/api/project/${P}/drawings/list`);
    const dl=await dr.json();
    if(dl.find(x=>x.spool_id===S)){
      document.getElementById('dwg-wrap').style.display='block';
      document.getElementById('dwg-btn').href=`/api/project/${P}/spool/${S}/drawing`;
    }
  }catch(e){}
}
async function toggle(n){
  const st=stepMap[n]||{completed:0};
  const newVal=st.completed?0:1;
  const op=document.getElementById('operator').value||'';
  const rem=document.querySelector(`#step-${n} .step-rem input`);
  const r=await fetch(`/api/project/${P}/spool/${S}/step/${n}`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({completed:newVal,operator:op,remarks:rem?rem.value:''})});
  const d=await r.json();
  if(d.ok) load();
}
async function remark(n,val){
  const st=stepMap[n]||{completed:0};
  const op=document.getElementById('operator').value||'';
  await fetch(`/api/project/${P}/spool/${S}/step/${n}`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({completed:st.completed?1:0,operator:st.completed_by||op,remarks:val})});
}
load();
</script></body></html>"""

REPORT_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ project }} — Report</title><style>""" + COMMON_CSS + """
.report-card{background:#fff;border-radius:12px;padding:16px;margin:12px 16px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.report-card h3{font-size:16px;color:#2F5496;margin-bottom:12px}
.status-badge{display:inline-block;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.status-on_time{background:#e8f5e9;color:#27ae60}.status-at_risk{background:#fff3e0;color:#f39c12}.status-delayed{background:#fce4ec;color:#e74c3c}.status-not_started{background:#f5f5f5;color:#95a5a6}
.diam-status{display:flex;flex-direction:column;gap:8px}
.diam-row{display:flex;align-items:center;gap:12px;padding:8px 12px;background:#FAFBFD;border-radius:8px}
.d-name{font-size:20px;font-weight:700;color:#2F5496;min-width:50px}.d-info{flex:1}.d-status{min-width:100px;text-align:right}
.gantt-mini{overflow-x:auto}
.gantt-table{border-collapse:collapse;width:100%;font-size:10px}
.gantt-table th{background:#404040;color:#fff;padding:4px 3px;font-size:9px;white-space:nowrap;text-align:center;min-width:45px}
.gantt-table td{padding:0;height:28px;position:relative;border:1px solid #f0f2f5;text-align:center;min-width:45px}
.gantt-table .g-label{font-weight:600;padding:4px 6px;text-align:left;white-space:nowrap;background:#fff;border-right:2px solid #e8e8e8}
.g-bar{position:absolute;top:2px;left:2px;right:2px;bottom:2px;border-radius:3px}
.g-exp-fab{background:#4472C4}.g-exp-paint{background:#ED7D31}.g-saved{background:#E2EFDA;border:1px dashed #A9D18E}
.g-forecast{background:transparent;border:2px dashed #e74c3c}
.g-today-line{position:absolute;left:50%;top:0;bottom:0;width:3px;background:#e74c3c;transform:translateX(-50%);z-index:10}
.g-pct{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:700;color:#fff;z-index:5}
.wk-current{background:#C00000!important;color:#fff!important}
.wk-dates{font-size:7px;font-weight:400;opacity:.7}
.mini-prog{width:100%;height:4px;background:#e8e8e8;border-radius:2px;margin-top:4px;overflow:hidden}
.mini-prog-fill{height:100%;border-radius:2px;background:#4472C4}
.act-item{padding:8px 12px;border-bottom:1px solid #f0f2f5;display:flex;gap:10px;align-items:center;font-size:13px}
.act-item .time{color:#888;font-size:11px;min-width:55px}.act-item .spool{font-weight:600;color:#2F5496;min-width:70px}
.act-item .detail{flex:1;color:#555}
.legend{display:flex;gap:12px;margin-top:10px;flex-wrap:wrap;font-size:10px;color:#666}
.legend span{display:flex;align-items:center;gap:4px}
.legend .box{width:14px;height:10px;border-radius:2px;display:inline-block}
.expected-bar{background:#e8e8e8;border-radius:6px;height:8px;position:relative;overflow:visible;margin-top:4px}
.expected-fill{position:absolute;left:0;top:0;height:100%;border-radius:6px;opacity:0.3;background:#2F5496}
.actual-fill{position:absolute;left:0;top:0;height:100%;border-radius:6px}
.commit-panel{background:#fff;border-radius:10px;padding:14px 18px;margin:12px 16px;box-shadow:0 2px 8px rgba(0,0,0,.08);display:flex;align-items:center;gap:16px;flex-wrap:wrap;border-left:4px solid #2F5496}
.commit-panel h4{font-size:12px;color:#2F5496;margin:0;white-space:nowrap}
.cp-item{text-align:center;padding:0 12px;border-right:1px solid #eee}.cp-item:last-child{border-right:none}
.cp-label{font-size:8px;color:#888;text-transform:uppercase}.cp-val{font-size:16px;font-weight:700}
.results-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:12px 16px}
.res-card{background:#fff;border-radius:12px;padding:20px 16px;text-align:center;border:2px dashed #d0d8e8}
.res-card.rc-blue{border-color:#4472C4;border-top:4px solid #2F5496}.res-card.rc-green{border-color:#27ae60;border-top:4px solid #27ae60}.res-card.rc-dark{border-color:#1F4E79;border-top:4px solid #1F4E79}
.res-card h5{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin:0 0 8px}
.res-card .rv{font-size:28px;font-weight:700}.res-card .rs{font-size:11px;color:#999;margin-top:6px;line-height:1.4}
.res-full{grid-column:1/-1}
@media(max-width:768px){.results-grid{grid-template-columns:repeat(2,1fr)}}
.transit-strip{background:#fff;border-radius:10px;padding:12px 18px;margin:10px 16px;box-shadow:0 1px 4px rgba(0,0,0,.06);display:flex;align-items:center;gap:16px;flex-wrap:wrap;border-left:4px solid #003366}
.sa-card{border:1px solid #f0f0f0;border-radius:8px;margin-bottom:6px;overflow:hidden}
.sa-header{display:flex;align-items:center;padding:8px 12px;gap:10px;cursor:pointer;user-select:none}
.sa-header:hover{background:#FAFBFD}
.sa-spool{font-weight:700;color:#2F5496;font-size:12px;min-width:65px}
.sa-dia{font-size:9px;color:#888;background:#f0f2f5;padding:1px 6px;border-radius:8px}
.sa-prog{width:60px;height:5px;background:#e8e8e8;border-radius:3px;overflow:hidden}
.sa-prog-fill{height:100%;border-radius:3px}
.sa-range{flex:1;font-size:11px;color:#555}.sa-range strong{color:#2F5496}
.sa-by{font-size:10px;color:#888}.sa-time{font-size:9px;color:#aaa;min-width:40px;text-align:right}
.sa-expand{font-size:9px;color:#ccc;transition:transform .2s}
.sa-card.open .sa-expand{transform:rotate(90deg)}
.sa-milestone{font-size:9px;font-weight:700;padding:2px 7px;border-radius:8px}
.sa-ms-rt{background:#EDE7F6;color:#5E35B1}.sa-ms-done{background:#E8F5E9;color:#2E7D32}
.sa-detail{display:none;border-top:1px solid #f5f5f5;background:#FAFBFD}
.sa-card.open .sa-detail{display:block}
.sa-drow{display:flex;align-items:center;padding:5px 12px 5px 36px;gap:8px;font-size:11px;border-bottom:1px solid #f5f5f5}
.sa-drow:last-child{border-bottom:none}
.act-summary{display:flex;background:#F8F9FB;border-radius:8px;padding:8px 0;margin-bottom:12px;flex-wrap:wrap}
.as-item{flex:1;text-align:center;padding:4px 12px;min-width:80px}
.as-item:not(:last-child){border-right:1px solid #e8e8e8}
.as-val{font-size:18px;font-weight:700}.as-lbl{font-size:9px;color:#888}
.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:12px 0}
.sum-card{text-align:center;padding:12px;border-radius:8px;background:#f8f9fa}
.sum-card .v{font-size:24px;font-weight:700}.sum-card .l{font-size:11px;color:#888;margin-top:2px}
@media print{.header{background:#2F5496!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}.no-print{display:none!important}}
</style></head><body>
<div class="header">
  <a class="back no-print" href="/project/{{ project }}">\u2190 Back / \u8fd4\u56de</a>
  <h1>Production Report / \u751f\u4ea7\u62a5\u544a</h1>
  <div class="sub">{{ project }} \u2014 <span id="rpt-date"></span></div>
</div>
<div id="rpt-content"><div style="text-align:center;padding:40px;color:#888">Loading report... / \u52a0\u8f7d\u62a5\u544a\u4e2d...</div></div>
<div style="padding:16px;text-align:center" class="no-print">
  <a class="btn" href="/api/project/{{ project }}/report/download">\U0001f4e5 Excel Report / Excel\u62a5\u544a</a>
  <a class="btn" href="/api/project/{{ project }}/report/pdf" style="margin-left:8px;background:#E74C3C">\U0001f4c4 PDF Report / PDF\u62a5\u544a</a>
  <button class="btn" onclick="window.print()" style="margin-left:8px">\U0001f5a8 Print / \u6253\u5370</button>
</div>
<script>
const P='{{project}}';
const STATUS_LABELS = {on_time:'ON TIME / \u6309\u65f6',at_risk:'AT RISK / \u6709\u5ef6\u8fdf\u98ce\u9669',delayed:'DELAYED / \u5df2\u5ef6\u8fdf',not_started:'NOT STARTED / \u672a\u5f00\u59cb'};
const STATUS_COLORS = {on_time:'#27ae60',at_risk:'#f39c12',delayed:'#e74c3c',not_started:'#95a5a6'};
async function load(){
  const r = await fetch(`/api/project/${P}/report`);
  const d = await r.json();
  document.getElementById('rpt-date').textContent = d.date;
  // Dynamic hold/release step detection from API
  const holdStepSet = new Set(d.hold_steps || []);
  const releaseStepSet = new Set(d.release_steps || []);
  let html = '';
  const st = d.stats, sch = d.schedule, sett = d.settings||{}, fc = d.forecast||{};
  const phases = d.phase_order || sch?.phase_order || ['fab'];
  const phaseColors = ['#4472C4', '#ED7D31', '#8E44AD', '#27AE60'];
  const overallStatus = sch ? sch.overall_status : 'not_started';
  const stdWeeks = parseInt(sett.standard_weeks||'9');
  const wksSaved = parseInt(sett.committed_weeks_saved||'0');
  const daysSaved = parseInt(sett.committed_days_saved||'0');
  const totalSaved = wksSaved*7+daysSaved;
  const hasExpediting = totalSaved > 0;
  const transitDays = parseInt(sett.sea_transit_days||'45');
  const toLocal = s => {const [y,m,d]=s.split('-');return new Date(+y,+m-1,+d);};
  const addDays = (dt,n) => new Date(dt.getFullYear(),dt.getMonth(),dt.getDate()+n);
  const fmt = dt => dt.toLocaleDateString('en',{day:'2-digit',month:'short',year:'numeric'});
  const fmtShort = dt => dt.toLocaleDateString('en',{day:'2-digit',month:'short'});

  html += `<div class="report-card">
    <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
      <div><h3 style="margin:0">Overall Status / \u603b\u4f53\u72b6\u6001</h3>
        <div class="status-badge status-${overallStatus}" style="margin-top:8px">${STATUS_LABELS[overallStatus]||overallStatus}</div></div>
      <div style="flex:1;min-width:200px"><div class="summary-grid">
        <div class="sum-card"><div class="v" style="color:#2F5496">${st.overall_pct}%</div><div class="l">Progress / \u8fdb\u5ea6</div></div>
        <div class="sum-card"><div class="v">${st.total}</div><div class="l">Total / \u603b\u6570</div></div>
        <div class="sum-card"><div class="v" style="color:#27ae60">${st.completed}</div><div class="l">Done / \u5b8c\u6210</div>${d.past_rt?`<div style="font-size:11px;color:#4472C4;margin-top:2px"><strong>${d.past_rt}</strong> past RT / \u5df2\u8fc7RT</div>`:''}</div>
        <div class="sum-card"><div class="v" style="color:#f39c12">${st.in_progress}</div><div class="l">WIP / \u8fdb\u884c\u4e2d</div></div>
        <div class="sum-card"><div class="v" style="color:#e74c3c">${st.not_started}</div><div class="l">Pending / \u5f85\u5f00\u59cb</div></div>
      </div></div>
    </div></div>`;

  if(sch && sch.diameters && sch.diameters.length){
    html += `<div class="report-card"><h3>Schedule Status by Diameter / \u6309\u7ba1\u5f84\u8ba1\u5212\u72b6\u6001</h3><div class="diam-status">`;
    const fcDiams = fc.diameters || {};
    sch.diameters.forEach(dm => {
      const color = STATUS_COLORS[dm.status] || '#95a5a6';
      const fdi = fcDiams[dm.diameter] || {};
      const dmPhaseAvgs = dm.phase_avgs || fdi.phase_avgs || {};
      const phaseInfo = phases.map((ph,pi) => `${ph.charAt(0).toUpperCase()+ph.slice(1)}: <strong>${dmPhaseAvgs[ph]||0}%</strong>`).join(' \u00b7 ');
      const phaseBars = phases.map((ph,pi) => `<div style="flex:1"><div style="font-size:8px;color:#aaa">${ph.charAt(0).toUpperCase()+ph.slice(1)}</div><div class="expected-bar"><div class="actual-fill" style="width:${dmPhaseAvgs[ph]||0}%;background:${phaseColors[pi%phaseColors.length]};border-radius:6px"></div></div></div>`).join('');
      html += `<div class="diam-row" style="border-left:4px solid ${color}">
        <div class="d-name">${dm.diameter}</div>
        <div class="d-info">
          <div style="font-size:12px;color:#888">${dm.spool_count} spools \u00b7 ${phaseInfo} \u00b7 Overall / \u603b: <strong>${dm.actual_pct}%</strong></div>
          <div style="display:flex;gap:4px;margin-top:6px">${phaseBars}</div>
          <div style="font-size:10px;color:#aaa;margin-top:2px">${fdi.remaining_raf?'RAF: '+fdi.remaining_raf+' in':''} ${fdi.remaining_m2?'\u00b7 Surface: '+fdi.remaining_m2+' m\u00b2':''}</div>
        </div>
        <div class="d-status"><span class="status-badge status-${dm.status}" style="font-size:11px;padding:4px 10px">${STATUS_LABELS[dm.status]||dm.status}</span></div>
      </div>`;
    });
    html += `</div></div>`;

    let prodStart = null;
    const starts = sch.diameters.map(x=>x.total_start).filter(x=>x).sort();
    if(starts.length) prodStart = starts[0];
    if(prodStart){
      const psDate = toLocal(prodStart);
      const stdEnd = addDays(psDate, stdWeeks*7 - 1);
      const commitEnd = hasExpediting ? addDays(stdEnd, -totalSaved) : stdEnd;
      const fcEnd = fc.overall_forecast_end ? toLocal(fc.overall_forecast_end) : null;
      const today = new Date(); today.setHours(0,0,0,0);

      if(hasExpediting){
        const diffDays = fcEnd ? Math.ceil((commitEnd - fcEnd) / 86400000) : 0;
        html += `<div class="commit-panel"><h4>\u26a1 Expediting Commitment / \u52a0\u6025\u627f\u8bfa</h4>
          <div class="cp-item"><div class="cp-label">Start / \u5f00\u59cb</div><div class="cp-val" style="color:#2F5496">${fmtShort(psDate)}</div></div>
          <div class="cp-item"><div class="cp-label">Standard End / \u6807\u51c6\u5b8c\u5de5</div><div class="cp-val" style="color:#888;text-decoration:line-through">${fmtShort(stdEnd)}</div></div>
          <div class="cp-item"><div class="cp-label">Committed End / \u627f\u8bfa\u5b8c\u5de5</div><div class="cp-val" style="color:#4472C4">${fmtShort(commitEnd)}</div></div>
          <div class="cp-item"><div class="cp-label">Saved / \u8282\u7701</div><div class="cp-val" style="color:#4472C4">${totalSaved}d</div></div>
          <div class="cp-item" style="border-right:none"><div class="cp-label">Forecast / \u9884\u6d4b</div><div class="cp-val" style="color:${diffDays>=0?'#27ae60':'#e74c3c'}">${fcEnd?fmtShort(fcEnd):'\u2014'} ${diffDays>=0?'\u2713':'\u2717'}</div></div>
        </div>`;
      }

      // Gantt
      const numWeeks = hasExpediting ? stdWeeks : Math.max(stdWeeks, Math.ceil(((fcEnd||stdEnd).getTime() - psDate.getTime()) / 86400000 / 7) + 1);
      html += `<div class="report-card"><h3>Production Gantt / \u751f\u4ea7\u7518\u7279\u56fe</h3>
        <div class="gantt-mini"><table class="gantt-table"><thead><tr>
        <th style="min-width:70px;background:#404040">Diameter</th><th style="min-width:45px;background:#404040">Phase</th>`;
      const weeks = [];
      for(let i=0;i<numWeeks;i++){
        const ws = addDays(psDate, i*7);
        const we = addDays(ws, 6);
        const isCurrent = today>=ws && today<=we;
        weeks.push({start:ws,end:we,num:i+1,current:isCurrent});
        html += `<th${isCurrent?' class="wk-current"':''}>W${i+1}<br><span class="wk-dates">${fmtShort(ws)} \u2192 ${fmtShort(we)}</span></th>`;
      }
      html += `</tr></thead><tbody>`;
      const ratio = hasExpediting ? (stdWeeks - wksSaved) / stdWeeks : 1;
      const lastDiamIdx = sch.diameters.length - 1;


      sch.diameters.forEach((dm, dmIdx) => {
        const fdi = fcDiams[dm.diameter] || {};
        const dmPhaseAvgs = fdi.phase_avgs || dm.phase_avgs || {};
        const overallP = fdi.overall_pct||0;
        const dmFcEnd = fdi.forecast_end ? toLocal(fdi.forecast_end) : null;
        const dmStarted = fdi.started;
        // Parse schedule dates from phase_dates
        const phaseDates = {};
        const dmPD = dm.phase_dates || {};
        phases.forEach(ph => {
          const pd = dmPD[ph];
          if(pd && pd.start && pd.end) phaseDates[ph] = {s:toLocal(pd.start), e:toLocal(pd.end)};
        });
        // Compute expedited dates per phase
        const expDates = {};
        let prevExpEnd = null;
        phases.forEach(ph => {
          if(!phaseDates[ph]) return;
          const {s:phS, e:phE} = phaseDates[ph];
          let expS, expE;
          if(hasExpediting){
            const daysDiffS = Math.round((phS-psDate)/86400000);
            const daysDiffE = Math.round((phE-psDate)/86400000);
            expS = addDays(psDate, Math.round(daysDiffS*ratio));
            expE = addDays(psDate, Math.round(daysDiffE*ratio));
            if(expE > commitEnd) expE = commitEnd;
            if(expS > commitEnd) expS = commitEnd;
            if(prevExpEnd && expS < prevExpEnd) expS = prevExpEnd;
            if(expE < expS) expE = expS;
          } else { expS = phS; expE = phE; }
          expDates[ph] = {s:expS, e:expE};
          prevExpEnd = expE;
        });
        const isLast = dmIdx===lastDiamIdx;
        // One row per phase
        html += `<tr>`;
        html += `<td class="g-label" rowspan="${phases.length}" style="color:#2F5496;font-size:13px"><b>${dm.diameter}</b> <span style="font-size:8px;color:#888;font-weight:400">${dm.spool_count} spools</span><div class="mini-prog" style="margin-top:2px"><div class="mini-prog-fill" style="width:${overallP}%"></div></div></td>`;
        phases.forEach((ph, pi) => {
          if(pi > 0) html += `<tr>`;
          const phP = dmPhaseAvgs[ph]||0;
          const phColor = phaseColors[pi % phaseColors.length];
          html += `<td class="g-label" style="font-size:9px;color:#666">${ph.charAt(0).toUpperCase()+ph.slice(1)}</td>`;
          const isLastPhase = pi === phases.length - 1;
          weeks.forEach(w => {
            const isToday = w.current;
            let content = '';
            if(phaseDates[ph] && expDates[ph]){
              const {s:phS, e:phE} = phaseDates[ph];
              const {s:expS, e:expE} = expDates[ph];
              const inStd = phS<=w.end && phE>=w.start;
              const inExp = expS<=w.end && expE>=w.start;
              const isSaved = hasExpediting && inStd && !inExp;
              const isForecast = isLastPhase && dmStarted && dmFcEnd && overallP<100 && dmFcEnd>=w.start && dmFcEnd<=w.end;
              if(inExp){ content = `<div class="g-bar" style="background:${phColor};position:absolute;top:2px;left:2px;right:2px;bottom:2px;border-radius:3px"></div>`;
                if(isToday) content += `<div class="g-today-line"></div><div class="g-pct">${phP}%</div>`;
                else if(w.end < today) content += `<div class="g-pct" style="color:#fff">\u2713</div>`;
              } else if(isSaved){ content = `<div class="g-bar g-saved"></div>`; }
              if(isForecast) content += `<div class="g-bar g-forecast"></div>`;
              if(isToday && !inExp){
                if(phP > 0 && phP < 100) content = `<div class="g-bar" style="background:${phColor};position:absolute;top:2px;left:2px;right:2px;bottom:2px;border-radius:3px"></div><div class="g-today-line"></div><div class="g-pct">${phP}%</div>`;
                else content += `<div class="g-today-line"></div>`;
              }
            } else {
              if(isToday) content += `<div class="g-today-line"></div>`;
            }
            if(isToday && isLast && isLastPhase) content += `<div style="position:absolute;bottom:-13px;left:50%;transform:translateX(-50%);font-size:7px;color:#e74c3c;font-weight:700;z-index:11">TODAY</div>`;
            html += `<td>${content}</td>`;
          });
          html += `</tr>`;
        });
        html += `<tr><td colspan="${numWeeks+2}" style="height:2px;background:#f0f2f5;border:none"></td></tr>`;
      });

      html += `</tbody></table></div>
        <div class="legend">
          ${phases.map((ph,pi) => `<span><span class="box" style="background:${phaseColors[pi%phaseColors.length]}"></span> ${ph.charAt(0).toUpperCase()+ph.slice(1)}</span>`).join('')}
          ${hasExpediting?'<span><span class="box" style="background:#E2EFDA;border:1px solid #A9D18E"></span> Saved / \u8282\u7701 \u2713</span>':''}
          <span><span class="box" style="border:2px dashed #e74c3c;width:12px;height:8px;display:inline-block;border-radius:2px"></span> Forecast / \u9884\u6d4b</span>
          <span><span class="box" style="background:#e74c3c;width:3px"></span> Today / \u4eca\u5929</span>
        </div></div>`;

      // Rate
      const actualWeld = fc.actual_weld_ipd||0, actualPaint = fc.actual_paint_m2d||0;
      const weldCap = fc.welding_capability||0, paintCap = fc.painting_capability||0;
      html += `<div class="report-card"><h3>Production Rate / \u751f\u4ea7\u7387</h3>
        <div style="display:flex;gap:20px;flex-wrap:wrap">
          <div style="flex:1;min-width:200px">
            <div style="font-size:12px;color:#888;margin-bottom:4px">Welding / \u710a\u63a5 (linear inches/day)</div>
            <div style="display:flex;align-items:baseline;gap:8px"><span style="font-size:24px;font-weight:700;color:${actualWeld>=weldCap?'#27ae60':'#e74c3c'}">${actualWeld}</span><span style="color:#888;font-size:12px">/ ${weldCap} target</span></div>
            <div class="expected-bar" style="margin-top:4px"><div class="actual-fill" style="width:${Math.min(actualWeld/Math.max(weldCap,1)*100,100)}%;background:${actualWeld>=weldCap?'#27ae60':'#e74c3c'}"></div></div>
          </div>
          ${paintCap > 0 ? `<div style="flex:1;min-width:200px">
            <div style="font-size:12px;color:#888;margin-bottom:4px">${phases.length>1?phases[phases.length-1].charAt(0).toUpperCase()+phases[phases.length-1].slice(1):'Surface'} / \u6d82\u88c5 (m\u00b2/day)</div>
            <div style="display:flex;align-items:baseline;gap:8px"><span style="font-size:24px;font-weight:700;color:${actualPaint>=paintCap?'#27ae60':'#e74c3c'}">${actualPaint}</span><span style="color:#888;font-size:12px">/ ${paintCap} target</span></div>
            <div class="expected-bar" style="margin-top:4px"><div class="actual-fill" style="width:${Math.min(actualPaint/Math.max(paintCap,1)*100,100)}%;background:${actualPaint>=paintCap?'#27ae60':'#e74c3c'}"></div></div>
          </div>` : ''}
        </div></div>`;

      // Results
      const fcSaved = fcEnd ? Math.ceil((stdEnd - fcEnd) / 86400000) : 0;
      const fcDiffCommit = fcEnd && hasExpediting ? Math.ceil((commitEnd - fcEnd) / 86400000) : 0;
      html += `<div class="results-grid">
        <div class="res-card rc-blue"><h5>Overall Progress / \u603b\u8fdb\u5ea6</h5><div class="rv" style="color:#2F5496">${st.overall_pct}%</div><div class="rs">${st.total} spools \u00b7 ${st.in_progress} WIP \u00b7 ${st.not_started} pending</div></div>
        ${hasExpediting?`<div class="res-card rc-blue"><h5>Production End / \u751f\u4ea7\u5b8c\u5de5</h5>
          <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin:4px 0">
            <span style="font-size:16px;color:#888;text-decoration:line-through">${fmtShort(stdEnd)}</span><span style="color:#888">\u2192</span>
            <span style="font-size:22px;font-weight:700;color:#4472C4">${fmtShort(commitEnd)}</span>
          </div><div class="rs">Standard \u2192 Committed (Expediting) / \u6807\u51c6\u2192\u627f\u8bfa</div></div>
        <div class="res-card rc-green"><h5>Expediting Commitment / \u52a0\u6025\u627f\u8bfa</h5><div class="rv" style="color:#27ae60">${totalSaved}<span style="font-size:14px;font-weight:400"> days</span></div><div class="rs">saved with expediting fee (${wksSaved} weeks) / \u52a0\u6025\u8282\u7701</div></div>
        <div class="res-card rc-green"><h5>Production Forecast / \u751f\u4ea7\u9884\u6d4b</h5><div class="rv" style="color:#27ae60">${fcSaved}<span style="font-size:14px;font-weight:400"> days</span></div><div class="rs">predicted savings \u00b7 ends ${fcEnd?fmtShort(fcEnd):'\u2014'}${fcDiffCommit>=0?' \u00b7 '+fcDiffCommit+' days ahead of commitment':''}</div></div>`
        :`<div class="res-card rc-blue"><h5>Forecast End / \u9884\u6d4b\u5b8c\u5de5</h5><div class="rv" style="color:#4472C4">${fcEnd?fmtShort(fcEnd):'\u2014'}</div><div class="rs">Based on actual rate / \u57fa\u4e8e\u5b9e\u9645\u8fdb\u5ea6</div></div>`}
        <div class="res-card rc-dark res-full"><h5>Actual End / \u5b9e\u9645\u5b8c\u5de5</h5><div class="rv" style="color:#2F5496">${st.completed>=st.total?fmtShort(new Date()):'\u2014'}</div><div class="rs">${st.completed>=st.total?'Production complete / \u751f\u4ea7\u5b8c\u6210':'Shown when production completes / \u751f\u4ea7\u5b8c\u6210\u540e\u663e\u793a'}</div></div>
      </div>`;

      // Transit
      const arrivalDate = fcEnd ? addDays(fcEnd, transitDays) : null;
      const commitArrival = hasExpediting ? addDays(commitEnd, transitDays) : null;
      html += `<div class="transit-strip">
        <div style="display:flex;align-items:center;gap:6px"><span style="font-size:18px">\U0001f6a2</span><div><div style="font-size:10px;color:#888;text-transform:uppercase">Sea Transit / \u6d77\u8fd0</div><div style="font-size:14px;font-weight:700;color:#003366">~${transitDays} days</div></div></div>
        ${hasExpediting?`<div style="width:1px;height:28px;background:#e0e0e0"></div>
        <div><div style="font-size:10px;color:#888;text-transform:uppercase">Expected Arrival Chile / \u9884\u8ba1\u5230\u8fbe\u667a\u5229</div><div style="font-size:14px;font-weight:700;color:#003366">${fmt(commitArrival)}</div><div style="font-size:9px;color:#999">Based on committed production end (${fmtShort(commitEnd)}) + ${transitDays} days</div></div>`:''}
        <div style="width:1px;height:28px;background:#e0e0e0"></div>
        <div><div style="font-size:10px;color:#888;text-transform:uppercase">Forecast Arrival Last Shipment / \u9884\u6d4b\u6700\u540e\u4e00\u6279\u5230\u8fbe</div><div style="font-size:14px;font-weight:700;color:#27ae60">${arrivalDate?fmt(arrivalDate):'\u2014'}</div><div style="font-size:9px;color:#999">Based on forecast production end${fcEnd?' ('+fmtShort(fcEnd)+')':''} + ${transitDays} days</div></div>
      </div>`;
    }
  } else {
    html += `<div class="report-card"><h3>Schedule Status / \u8ba1\u5212\u72b6\u6001</h3>
      <p style="color:#888;padding:20px 0">No schedule configured.<br><code>POST /api/project/${P}/schedule</code></p></div>`;
  }

  // Today's activity — grouped by spool, using dynamic hold/release
  const completed = (d.today_activity||[]).filter(a=>a.action==='completed');
  const stepNames = d.step_names||{};
  const spoolPcts = d.spool_progress||{};
  const groups = {};
  completed.forEach(a => { if(!groups[a.spool_id]) groups[a.spool_id]=[]; groups[a.spool_id].push(a); });
  const spoolKeys = Object.keys(groups);

  html += `<div class="report-card"><h3>Today's Activity / \u4eca\u65e5\u52a8\u6001 <span style="font-weight:400;color:#888;font-size:12px">(${d.steps_completed_today} steps)</span></h3>`;
  html += `<div class="act-summary">
    <div class="as-item"><div class="as-val" style="color:#2F5496">${d.steps_completed_today}</div><div class="as-lbl">Steps / \u6b65\u9aa4</div></div>
    <div class="as-item"><div class="as-val" style="color:#4472C4">${spoolKeys.length}</div><div class="as-lbl">Spools / \u7ba1\u6bb5</div></div>
    <div class="as-item"><div class="as-val" style="color:#27ae60">${d.released_today||0}</div><div class="as-lbl">Released / \u653e\u884c</div></div>
    <div class="as-item"><div class="as-val" style="color:#5E35B1">${d.past_rt||0}</div><div class="as-lbl">Past RT / \u8fc7RT</div></div>
  </div>`;

  if(spoolKeys.length){
    const showLimit = 15;
    spoolKeys.forEach((sid,idx) => {
      const items = groups[sid];
      const pct = spoolPcts[sid]||0;
      const first = items[items.length-1], last = items[0];
      const range = items.length===1 ? (stepNames[first.step_number]||'Step '+first.step_number) : (stepNames[first.step_number]||'Step '+first.step_number)+' \u2192 '+(stepNames[last.step_number]||'Step '+last.step_number);
      const ts = (last.timestamp||'').substring(11,16);
      const hasRT = items.some(a=>holdStepSet.has(a.step_number));
      const hasRelease = items.some(a=>releaseStepSet.has(a.step_number));
      const barColor = pct>=100?'#27ae60':pct>60?'#4472C4':pct>0?'#f39c12':'#ccc';
      const hidden = idx>=showLimit ? ' style="display:none" data-extra' : '';
      html += `<div class="sa-card"${hidden} onclick="this.classList.toggle('open')">
        <div class="sa-header">
          <div class="sa-spool">${sid}</div>
          <div class="sa-prog"><div class="sa-prog-fill" style="width:${pct}%;background:${barColor}"></div></div>
          <div class="sa-range"><strong>${items.length}</strong> \u00b7 ${range}</div>
          ${hasRT?'<div class="sa-milestone sa-ms-rt">\u2605 RT</div>':''}
          ${hasRelease?'<div class="sa-milestone sa-ms-done">\U0001f3c1 RELEASED</div>':''}
          <div class="sa-by">${last.operator||''}</div><div class="sa-time">${ts}</div><div class="sa-expand">\u25b8</div>
        </div>
        <div class="sa-detail">${items.map(a=>{
          const sn=stepNames[a.step_number]||'Step '+a.step_number;
          const t=(a.timestamp||'').substring(11,19);
          const icon=releaseStepSet.has(a.step_number)?'\U0001f3c1':holdStepSet.has(a.step_number)?'\u2b50':'\u2705';
          return `<div class="sa-drow"><span style="color:#aaa;font-size:10px;min-width:50px">${t}</span><span>${icon}</span><span style="flex:1;color:#555">${sn}</span><span style="color:#888;font-size:10px">${a.operator||''}</span></div>`;
        }).join('')}</div></div>`;
    });
    if(spoolKeys.length>showLimit) html += `<div style="text-align:center;padding:10px;color:#4472C4;font-size:12px;font-weight:600;cursor:pointer" onclick="document.querySelectorAll('[data-extra]').forEach(e=>e.style.display='');this.style.display='none'">Show all ${spoolKeys.length} spools / \u663e\u793a\u5168\u90e8 \u25be</div>`;
  } else {
    html += `<div style="text-align:center;padding:20px;color:#aaa">No activity today / \u4eca\u5929\u6682\u65e0\u52a8\u6001</div>`;
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
