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

# Legacy 424 steps — used ONLY as fallback seed data during migration
_LEGACY_424_STEPS = [
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
        rows = _LEGACY_424_STEPS
    setattr(g, cache_key, rows)
    return rows

def get_project_settings(project):
    """Get project settings with defaults."""
    rows = db_fetchall("SELECT key, value FROM project_settings WHERE project=?", (project,))
    settings = {r['key']: r['value'] for r in rows}
    defaults = {'committed_weeks_saved':'0', 'committed_days_saved':'0', 'sea_transit_days':'45',
                'standard_weeks':'9', 'welding_capability_ipd':'1000', 'painting_capability_m2d':'91',
                'spools_per_day':'{}', 'painting_days':'13',
                'fab_label':'Fab / \u5236\u4f5c', 'paint_label':'Paint / \u6d82\u88c5'}
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
def spool_hours(spool_row, completed_steps, settings, steps_def):
    """Calculate hours-based progress for a single spool using dynamic step definitions."""
    raf = float(spool_row.get('raf_inches') or 0)
    surface = float(spool_row.get('surface_m2') or 0)
    has_br = spool_row.get('has_branches', 0)
    spool_type = spool_row.get('spool_type', 'SPOOL') or 'SPOOL'
    weld_cap = float(settings.get('welding_capability_ipd', '552'))
    paint_cap = float(settings.get('painting_capability_m2d', '91'))

    # Pre-count surface steps per phase for even splitting
    surface_count_by_phase = {}
    for step in steps_def:
        if step['hours_variable'] == 'surface' and step['phase']:
            surface_count_by_phase[step['phase']] = surface_count_by_phase.get(step['phase'], 0) + 1

    fab_total = 0.0; fab_done = 0.0
    paint_total = 0.0; paint_done = 0.0
    weld_hrs = 0.0; surface_hrs = 0.0

    for step in steps_def:
        sn = step['step_number']
        # Skip steps not applicable to this spool
        if step['is_conditional'] and not has_br:
            continue
        st = step.get('spool_type', 'ALL') or 'ALL'
        if st != 'ALL' and st != spool_type:
            continue

        # Calculate hours for this step
        if step['hours_variable'] == 'welding':
            hrs = (raf / weld_cap * 8) if weld_cap > 0 and raf > 0 else 0
            weld_hrs = hrs
        elif step['hours_variable'] == 'surface':
            if surface <= 0:
                continue  # skip surface steps if no painting
            n_surface = surface_count_by_phase.get(step['phase'], 1)
            total_surface_hrs = (surface * 0.98 / paint_cap * 8) if paint_cap > 0 else 0
            hrs = total_surface_hrs / n_surface if n_surface > 0 else 0
            surface_hrs += hrs
        else:
            # Fixed hours — skip paint-phase fixed steps if no surface
            if step['phase'] == 'paint' and surface <= 0:
                continue
            hrs = float(step.get('hours_fixed', 2.0) or 2.0)

        # Accumulate by phase
        if step['phase'] == 'fab':
            fab_total += hrs
            if sn in completed_steps: fab_done += hrs
        else:
            paint_total += hrs
            if sn in completed_steps: paint_done += hrs

    total = fab_total + paint_total
    done = fab_done + paint_done
    pct = round(done / total * 100, 1) if total > 0 else 0.0
    fab_pct = round(fab_done / fab_total * 100, 1) if fab_total > 0 else 0.0
    paint_pct = round(paint_done / paint_total * 100, 1) if paint_total > 0 else 0.0

    return {
        'fab_total': fab_total, 'fab_done': fab_done, 'fab_pct': fab_pct,
        'paint_total': paint_total, 'paint_done': paint_done, 'paint_pct': paint_pct,
        'total': total, 'done': done, 'pct': pct,
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
    bulk = bulk_spool_progress(project, settings)
    spools = [v for v in bulk.values()]
    total = len(spools)
    st = {'total':total,'completed':0,'in_progress':0,'not_started':0,'overall_pct':0.0,'by_diameter':{},'by_line':{}}
    tp = 0
    for v in spools:
        p = v['pct']; tp += p; s = v['spool']
        if p>=100: st['completed']+=1
        elif p>0: st['in_progress']+=1
        else: st['not_started']+=1
        d = s['main_diameter'] or '?'
        if d not in st['by_diameter']: st['by_diameter'][d] = {'total':0,'pct_sum':0,'fab_pct_sum':0,'paint_pct_sum':0}
        st['by_diameter'][d]['total']+=1; st['by_diameter'][d]['pct_sum']+=p
        st['by_diameter'][d]['fab_pct_sum']+=v['fab_pct']; st['by_diameter'][d]['paint_pct_sum']+=v['paint_pct']
        l = s['line'] or '?'
        if l not in st['by_line']: st['by_line'][l] = {'total':0,'pct_sum':0}
        st['by_line'][l]['total']+=1; st['by_line'][l]['pct_sum']+=p
    if total: st['overall_pct'] = round(tp/total,1)
    for v in st['by_diameter'].values():
        v['avg_pct'] = round(v['pct_sum']/v['total'],1) if v['total'] else 0
        v['fab_avg_pct'] = round(v['fab_pct_sum']/v['total'],1) if v['total'] else 0
        v['paint_avg_pct'] = round(v['paint_pct_sum']/v['total'],1) if v['total'] else 0
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
        fab = sm.get('fabrication', sm.get('Fabricacion', {}))
        paint = sm.get('painting', sm.get('Pintura', {}))
        if not fab: continue
        try:
            fab_start = parse_date(fab['start']); fab_end = parse_date(fab['end'])
            if not fab_start or not fab_end: continue
            if paint:
                paint_end = parse_date(paint['end'])
                total_end = paint_end if paint_end else fab_end
            else:
                total_end = fab_end
            target_end = committed_end if committed_end else total_end
            total_days = max(1, (target_end - fab_start).days)
            elapsed = max(0, min((today - fab_start).days, total_days))
            expected_pct = round(elapsed / total_days * 100, 1) if total_days > 0 else 0
        except: continue
        diam_spools = by_diam.get(dk, by_diam.get(f'{diam}"', []))
        if not diam_spools: continue
        actual_sum = sum(bulk.get(s['spool_id'], {}).get('pct', 0) for s in diam_spools)
        actual_pct = round(actual_sum / len(diam_spools), 1)
        fab_sum = sum(bulk.get(s['spool_id'], {}).get('fab_pct', 0) for s in diam_spools)
        paint_sum = sum(bulk.get(s['spool_id'], {}).get('paint_pct', 0) for s in diam_spools)
        fab_avg = round(fab_sum / len(diam_spools), 1)
        paint_avg = round(paint_sum / len(diam_spools), 1)
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
        remaining_raf = sum(bulk.get(s['spool_id'], {}).get('raf_inches', 0) for s in diam_spools if bulk.get(s['spool_id'], {}).get('fab_pct', 0) < 100)
        remaining_m2 = sum(float(s.get('surface_m2') or 0) * 0.98 for s in diam_spools if bulk.get(s['spool_id'], {}).get('paint_pct', 0) < 100)
        result.append({
            'diameter': dk, 'spool_count': len(diam_spools),
            'expected_pct': expected_pct, 'actual_pct': actual_pct, 'diff': round(diff, 1), 'status': status,
            'fab_pct': fab_avg, 'paint_pct': paint_avg,
            'remaining_raf': round(remaining_raf, 0), 'remaining_m2': round(remaining_m2, 1),
            'fab_start': fab.get('start',''), 'fab_end': fab.get('end',''),
            'paint_start': paint.get('start','') if paint else '', 'paint_end': paint.get('end','') if paint else '',
            'total_start': fab.get('start',''), 'total_end': str(total_end),
        })
    statuses = [r['status'] for r in result if r['status'] != 'not_started']
    if 'delayed' in statuses: overall_status = 'delayed'
    elif 'at_risk' in statuses: overall_status = 'at_risk'
    elif statuses: overall_status = 'on_time'
    else: overall_status = 'not_started'
    return {'diameters': result, 'overall_status': overall_status, 'today': str(today)}

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
    diam_order = get_diameter_order(project)
    weld_cap = float(settings.get('welding_capability_ipd', '1000'))
    paint_cap = float(settings.get('painting_capability_m2d', '91'))
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
        fab_pct = sum(i['fab_pct'] for i in diam_infos) / len(diam_infos)
        paint_pct = sum(i['paint_pct'] for i in diam_infos) / len(diam_infos)
        overall_pct = done_hrs / total_hrs * 100 if total_hrs > 0 else 0
        started = done_hrs > 0
        remaining_raf = sum(i['raf_inches'] for i in diam_infos if i['fab_pct'] < 100)
        remaining_m2 = sum(i['surface_m2'] * 0.98 for i in diam_infos if i['paint_pct'] < 100)
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
            'fab_pct': round(fab_pct, 1), 'paint_pct': round(paint_pct, 1),
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
    if USE_PG:
        db_execute("DELETE FROM drawings WHERE NOT EXISTS (SELECT 1 FROM spools WHERE spools.project=drawings.project AND spools.spool_id=drawings.spool_id)")
    else:
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
    """Import schedule data. Accepts JSON array or {fab_start} for auto-calculation."""
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
    elif isinstance(data, dict) and 'fab_start' in data:
        fab_start = date.fromisoformat(data['fab_start'])
        settings = get_project_settings(project)
        spd = json.loads(settings.get('spools_per_day', '{}'))
        painting_days = int(settings.get('painting_days', '13'))
        diam_order = get_diameter_order(project)
        spools = db_fetchall("SELECT main_diameter FROM spools WHERE project=?", (project,))
        diam_counts = {}
        for s in spools:
            d = (s['main_diameter'] or '?').replace('"','')
            if d not in diam_counts: diam_counts[d] = 0
            diam_counts[d] += 1
        current_fab = fab_start
        for diam in diam_order:
            if diam not in diam_counts: continue
            cnt = diam_counts[diam]
            rate = float(spd.get(diam, 2.0))
            fab_days = max(1, round(cnt / rate))
            fab_end = current_fab + timedelta(days=fab_days)
            paint_start = fab_end + timedelta(days=1)
            paint_end = paint_start + timedelta(days=painting_days)
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
        fl = sett.get('fab_label', 'Fab').split('/')[0].strip()
        pl = sett.get('paint_label', 'Paint').split('/')[0].strip()
        headers = ['Diameter','Spools',f'{fl} %',f'{pl} %','Overall %','Diff (days)','Status',f'{fl} Start',f'{fl} End',f'{pl} End','Forecast End']
        for col, h in enumerate(headers, 1):
            c = ws.cell(row, col, h); c.font = hf; c.fill = hfill; c.alignment = Alignment(horizontal='center', wrap_text=True); c.border = thin
        row += 1
        for d in sched['diameters']:
            dk = d['diameter']; fcd = fc_diams.get(dk, {})
            ws.cell(row, 1, dk).font = bfb; ws.cell(row, 1).border = thin
            ws.cell(row, 2, d['spool_count']).font = bf; ws.cell(row, 2).alignment = center; ws.cell(row, 2).border = thin
            c3 = ws.cell(row, 3, d.get('fab_pct', 0)); c3.font = bfb; c3.alignment = center; c3.border = thin
            if d.get('fab_pct', 0) >= 100: c3.fill = green_fill
            c4 = ws.cell(row, 4, d.get('paint_pct', 0)); c4.font = bfb; c4.alignment = center; c4.border = thin
            if d.get('paint_pct', 0) >= 100: c4.fill = green_fill
            ws.cell(row, 5, d['actual_pct']).font = bfb; ws.cell(row, 5).alignment = center; ws.cell(row, 5).border = thin
            diff_val = d['diff']; diff_label = f"+{diff_val}d" if diff_val > 0 else f"{diff_val}d" if diff_val < 0 else "0d"
            c6 = ws.cell(row, 6, diff_label); c6.alignment = center; c6.border = thin
            c6.font = Font(size=10, color='27AE60' if diff_val > 0 else 'E74C3C' if diff_val < 0 else '333333')
            sc = ws.cell(row, 7, status_label.get(d['status'], d['status']))
            sc.font = bfb; sc.alignment = center; sc.border = thin
            if d['status'] == 'on_time': sc.fill = green_fill
            elif d['status'] == 'at_risk': sc.fill = orange_fill
            elif d['status'] == 'delayed': sc.fill = red_fill
            ws.cell(row, 8, d['fab_start']).font = bf; ws.cell(row, 8).border = thin
            ws.cell(row, 9, d['fab_end']).font = bf; ws.cell(row, 9).border = thin
            ws.cell(row, 10, d.get('paint_end','')).font = bf; ws.cell(row, 10).border = thin
            ws.cell(row, 11, fcd.get('forecast_end', '')).font = bf; ws.cell(row, 11).border = thin
            row += 1
        row += 1
        # Expediting + Gantt + Rate + Results + Transit — same as before
        prod_start = None
        starts = [d['fab_start'] for d in sched['diameters'] if d['fab_start']]
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
            fab_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            paint_fill = PatternFill(start_color='ED7D31', end_color='ED7D31', fill_type='solid')
            saved_fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
            forecast_fill = PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid')
            today_border = Border(left=Side('thick',color='FF0000'),right=Side('thick',color='FF0000'),top=Side('thin',color='C0C0C0'),bottom=Side('thin',color='C0C0C0'))
            today_bar_border = Border(left=Side('thick',color='FF0000'),right=Side('thick',color='FF0000'),top=Side('medium',color='333333'),bottom=Side('medium',color='333333'))
            for d in sched['diameters']:
                dk = d['diameter']; fcd = fc_diams.get(dk, {})
                fab_pct = fcd.get('fab_pct', 0) or 0; paint_pct = fcd.get('paint_pct', 0) or 0
                overall_pct = fcd.get('overall_pct', 0) or 0; dm_started = fcd.get('started', False)
                dm_fc_end_str = fcd.get('forecast_end', ''); dm_fc_end = date.fromisoformat(dm_fc_end_str) if dm_fc_end_str else None
                fab_ps = date.fromisoformat(d['fab_start']); fab_pe = date.fromisoformat(d['fab_end'])
                paint_ps_str = d.get('paint_start',''); paint_pe_str = d.get('paint_end','')
                paint_ps = date.fromisoformat(paint_ps_str) if paint_ps_str else None
                paint_pe = date.fromisoformat(paint_pe_str) if paint_pe_str else None
                if has_expediting and commit_end:
                    exp_fab_s = prod_start + timedelta(days=(fab_ps - prod_start).days * ratio)
                    exp_fab_e = prod_start + timedelta(days=(fab_pe - prod_start).days * ratio)
                    if exp_fab_e > commit_end: exp_fab_e = commit_end
                    if paint_ps and paint_pe:
                        exp_paint_s = prod_start + timedelta(days=(paint_ps - prod_start).days * ratio)
                        exp_paint_e = prod_start + timedelta(days=(paint_pe - prod_start).days * ratio)
                        if exp_paint_s < exp_fab_e: exp_paint_s = exp_fab_e
                        if exp_paint_e < exp_paint_s: exp_paint_e = exp_paint_s
                        if exp_paint_e > commit_end: exp_paint_e = commit_end
                    else: exp_paint_s = None; exp_paint_e = None
                else:
                    exp_fab_s = fab_ps; exp_fab_e = fab_pe; exp_paint_s = paint_ps; exp_paint_e = paint_pe
                # FAB ROW
                ws.cell(row, 1, dk).font = Font(bold=True, size=11, color='2F5496'); ws.cell(row, 1).border = thin
                ws.cell(row, 2, fl).font = Font(size=9, color='666666'); ws.cell(row, 2).border = thin
                pct_cell = ws.cell(row, 3)
                if fab_pct >= 100: pct_cell.value = '\u2713'; pct_cell.font = Font(bold=True, size=10, color='27AE60')
                elif fab_pct > 0: pct_cell.value = f'{fab_pct:.0f}%'; pct_cell.font = Font(bold=True, size=8, color='4472C4')
                else: pct_cell.value = '-'; pct_cell.font = Font(size=8, color='AAAAAA')
                pct_cell.alignment = center; pct_cell.border = thin
                for i, (ws_d, we_d) in enumerate(weeks):
                    col = 4 + i; cell = ws.cell(row, col); cell.border = thin
                    in_std = fab_ps <= we_d and fab_pe >= ws_d
                    in_exp = exp_fab_s <= we_d and exp_fab_e >= ws_d
                    is_saved = has_expediting and in_std and not in_exp
                    is_today_col = today_col and col == today_col
                    if in_exp:
                        cell.fill = fab_fill
                        if is_today_col and 0 < fab_pct < 100: cell.value = f'{fab_pct:.0f}%'; cell.font = Font(bold=True, size=7, color='FFFFFF'); cell.alignment = center
                        elif fab_pct >= 100 and we_d < today: cell.value = '\u2713'; cell.font = Font(bold=True, size=8, color='FFFFFF'); cell.alignment = center
                    elif is_saved:
                        cell.fill = saved_fill; cell.value = '\u2713'; cell.font = Font(size=7, color='A9D18E'); cell.alignment = center
                    if is_today_col: cell.border = today_bar_border if in_exp else today_border
                row += 1
                # PAINT ROW
                ws.cell(row, 1, '').border = thin
                ws.cell(row, 2, pl).font = Font(size=9, color='666666'); ws.cell(row, 2).border = thin
                pct_cell = ws.cell(row, 3)
                if paint_pct >= 100: pct_cell.value = '\u2713'; pct_cell.font = Font(bold=True, size=10, color='27AE60')
                elif paint_pct > 0: pct_cell.value = f'{paint_pct:.0f}%'; pct_cell.font = Font(bold=True, size=8, color='ED7D31')
                else: pct_cell.value = '-'; pct_cell.font = Font(size=8, color='AAAAAA')
                pct_cell.alignment = center; pct_cell.border = thin
                for i, (ws_d, we_d) in enumerate(weeks):
                    col = 4 + i; cell = ws.cell(row, col); cell.border = thin
                    in_std_paint = paint_ps and paint_pe and paint_ps <= we_d and paint_pe >= ws_d
                    in_exp_paint = exp_paint_s and exp_paint_e and exp_paint_s <= we_d and exp_paint_e >= ws_d
                    in_std_fab = fab_ps <= we_d and fab_pe >= ws_d
                    in_exp_fab = exp_fab_s <= we_d and exp_fab_e >= ws_d
                    is_saved = has_expediting and (in_std_paint or in_std_fab) and not in_exp_paint and not in_exp_fab
                    is_today_col = today_col and col == today_col
                    is_forecast = dm_started and dm_fc_end and overall_pct < 100 and dm_fc_end >= ws_d and dm_fc_end <= we_d
                    if in_exp_paint:
                        cell.fill = paint_fill
                        if is_today_col and 0 < paint_pct < 100: cell.value = f'{paint_pct:.0f}%'; cell.font = Font(bold=True, size=7, color='FFFFFF'); cell.alignment = center
                        elif paint_pct >= 100 and we_d < today: cell.value = '\u2713'; cell.font = Font(bold=True, size=8, color='FFFFFF'); cell.alignment = center
                    elif is_saved:
                        cell.fill = saved_fill; cell.value = '\u2713'; cell.font = Font(size=7, color='A9D18E'); cell.alignment = center
                    elif is_forecast:
                        cell.fill = forecast_fill; cell.value = '\u25c6'; cell.font = Font(size=8, color='C00000'); cell.alignment = center
                    if is_today_col: cell.border = today_bar_border if in_exp_paint else today_border
                row += 1
            row += 1
            ws.cell(row, 1, 'Legend:').font = Font(bold=True, size=9)
            lg = ws.cell(row, 2, fl); lg.fill = fab_fill; lg.font = Font(size=8, color='FFFFFF'); lg.alignment = center
            lg = ws.cell(row, 3, pl); lg.fill = paint_fill; lg.font = Font(size=8, color='FFFFFF'); lg.alignment = center
            if has_expediting:
                lg = ws.cell(row, 4, 'Saved \u2713'); lg.fill = saved_fill; lg.font = Font(size=8, color='A9D18E'); lg.alignment = center
                lg = ws.cell(row, 5, '\u25c6 Forecast'); lg.fill = forecast_fill; lg.font = Font(size=8, color='C00000'); lg.alignment = center
                ws.cell(row, 6, '| Today |').font = Font(bold=True, size=8, color='FF0000')
            else:
                lg = ws.cell(row, 4, '\u25c6 Forecast'); lg.fill = forecast_fill; lg.font = Font(size=8, color='C00000'); lg.alignment = center
                ws.cell(row, 5, '| Today |').font = Font(bold=True, size=8, color='FF0000')
            row += 2
        # Production Rate
        actual_weld = fc_data.get('actual_weld_ipd', 0) or 0
        actual_paint = fc_data.get('actual_paint_m2d', 0) or 0
        weld_cap = fc_data.get('welding_capability', 0) or 0
        paint_cap = fc_data.get('painting_capability', 0) or 0
        ws.cell(row, 1, "PRODUCTION RATE / \u751f\u4ea7\u7387").font = Font(bold=True, size=12, color='2F5496')
        row += 1
        rate_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
        for label, actual, target, unit in [
            ('Welding / \u710a\u63a5', actual_weld, weld_cap, 'linear inches/day'),
            (sett.get('paint_label', 'Paint / \u6d82\u88c5'), actual_paint, paint_cap, 'm\u00b2/day'),
        ]:
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
  const fabLabel = sett.fab_label || 'Fab / \u5236\u4f5c';
  const paintLabel = sett.paint_label || 'Paint / \u6d82\u88c5';
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
    const starts = schd.diameters.map(x=>x.fab_start).filter(x=>x).sort();
    if(starts.length){
      const psDate = new Date(starts[0]);
      const stdEnd = new Date(psDate.getTime() + stdWeeks*7*86400000 - 86400000);
      const commitEnd = new Date(stdEnd.getTime() - totalSaved*86400000);
      const fcEnd = fc.overall_forecast_end ? new Date(fc.overall_forecast_end) : null;
      const today = new Date(); today.setHours(0,0,0,0);
      const daysToTarget = Math.ceil((commitEnd - today) / 86400000);
      const fcSaved = fcEnd ? Math.ceil((stdEnd - fcEnd) / 86400000) : 0;
      const fcDiff = fcEnd ? Math.ceil((commitEnd - fcEnd) / 86400000) : 0;
      const fmt = d => d.toLocaleDateString('en',{day:'2-digit',month:'short'});
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
    return `<div class="diam-card ${cls}"><div class="pace-badge ${badgeCls}">${badge}</div><div class="d">${d}</div><div class="p">${v.total} spools</div>
      <div class="pbar-bg" style="margin-top:6px"><div class="pbar-fill" style="width:${v.avg_pct}%;background:${barColor}"></div></div>
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
<div class="prog"><div class="big" id="prog-pct">--</div><div class="lbl">Progress / \u8fdb\u5ea6</div>
  <div class="pbar-bg" style="max-width:300px;margin:8px auto"><div class="pbar-fill" id="prog-bar" style="width:0%;background:#2F5496"></div></div>
</div>
<div class="op-input"><input id="operator" placeholder="Operator name / \u64cd\u4f5c\u5458\u59d3\u540d" value=""></div>
<div class="checklist" id="steps"></div>
<div style="padding:16px;text-align:center">
  <a class="btn" id="dwg-btn" style="display:none" target="_blank">\U0001f4c4 View Drawing / \u67e5\u770b\u56fe\u7eb8</a>
</div>
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
      const btn=document.getElementById('dwg-btn');btn.style.display='inline-block';
      btn.href=`/api/project/${P}/spool/${S}/drawing`;
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
.gantt-table td{padding:0;height:22px;position:relative;border:1px solid #f0f2f5;text-align:center;min-width:45px}
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
  const fabLabel = sett.fab_label || 'Fab / \u5236\u4f5c';
  const paintLabel = sett.paint_label || 'Paint / \u6d82\u88c5';
  const overallStatus = sch ? sch.overall_status : 'not_started';
  const stdWeeks = parseInt(sett.standard_weeks||'9');
  const wksSaved = parseInt(sett.committed_weeks_saved||'0');
  const daysSaved = parseInt(sett.committed_days_saved||'0');
  const totalSaved = wksSaved*7+daysSaved;
  const hasExpediting = totalSaved > 0;
  const transitDays = parseInt(sett.sea_transit_days||'45');
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
      const fabP = dm.fab_pct||fdi.fab_pct||0, paintP = dm.paint_pct||fdi.paint_pct||0;
      html += `<div class="diam-row" style="border-left:4px solid ${color}">
        <div class="d-name">${dm.diameter}</div>
        <div class="d-info">
          <div style="font-size:12px;color:#888">${dm.spool_count} spools \u00b7 ${fabLabel}: <strong>${fabP}%</strong> \u00b7 ${paintLabel}: <strong>${paintP}%</strong> \u00b7 Overall / \u603b: <strong>${dm.actual_pct}%</strong></div>
          <div style="display:flex;gap:4px;margin-top:6px">
            <div style="flex:1"><div style="font-size:8px;color:#aaa">${fabLabel}</div><div class="expected-bar"><div class="actual-fill" style="width:${fabP}%;background:#4472C4;border-radius:6px"></div></div></div>
            <div style="flex:1"><div style="font-size:8px;color:#aaa">${paintLabel}</div><div class="expected-bar"><div class="actual-fill" style="width:${paintP}%;background:#ED7D31;border-radius:6px"></div></div></div>
          </div>
          <div style="font-size:10px;color:#aaa;margin-top:2px">${fdi.remaining_raf?'RAF: '+fdi.remaining_raf+' in':''} ${fdi.remaining_m2?'\u00b7 Surface: '+fdi.remaining_m2+' m\u00b2':''}</div>
        </div>
        <div class="d-status"><span class="status-badge status-${dm.status}" style="font-size:11px;padding:4px 10px">${STATUS_LABELS[dm.status]||dm.status}</span></div>
      </div>`;
    });
    html += `</div></div>`;

    let prodStart = null;
    const starts = sch.diameters.map(x=>x.fab_start).filter(x=>x).sort();
    if(starts.length) prodStart = starts[0];
    if(prodStart){
      const psDate = new Date(prodStart);
      const stdEnd = new Date(psDate.getTime() + stdWeeks*7*86400000 - 86400000);
      const commitEnd = hasExpediting ? new Date(stdEnd.getTime() - totalSaved*86400000) : stdEnd;
      const fcEnd = fc.overall_forecast_end ? new Date(fc.overall_forecast_end) : null;
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
        const ws = new Date(psDate.getTime()+i*7*86400000);
        const we = new Date(ws.getTime()+6*86400000);
        const isCurrent = today>=ws && today<=we;
        weeks.push({start:ws,end:we,num:i+1,current:isCurrent});
        html += `<th${isCurrent?' class="wk-current"':''}>W${i+1}<br><span class="wk-dates">${fmtShort(ws)} \u2192 ${fmtShort(we)}</span></th>`;
      }
      html += `</tr></thead><tbody>`;
      const ratio = hasExpediting ? (stdWeeks - wksSaved) / stdWeeks : 1;
      const lastDiamIdx = sch.diameters.length - 1;
      const DAY = 86400000;

      sch.diameters.forEach((dm, dmIdx) => {
        const fdi = fcDiams[dm.diameter] || {};
        const fabP = fdi.fab_pct||0, paintP = fdi.paint_pct||0, overallP = fdi.overall_pct||0;
        const dmFcEnd = fdi.forecast_end ? new Date(fdi.forecast_end) : null;
        const dmStarted = fdi.started;
        const fabPs = new Date(dm.fab_start), fabPe = new Date(dm.fab_end);
        const paintPs = new Date(dm.paint_start), paintPe = new Date(dm.paint_end);
        let expFabStart, expFabEnd, expPaintStart, expPaintEnd;
        if(hasExpediting){
          expFabStart = new Date(Math.min(psDate.getTime() + (fabPs-psDate)*ratio, commitEnd.getTime()));
          expFabEnd = new Date(Math.min(psDate.getTime() + (fabPe-psDate)*ratio, commitEnd.getTime()));
          expPaintStart = new Date(Math.min(psDate.getTime() + (paintPs-psDate)*ratio, commitEnd.getTime()));
          expPaintEnd = new Date(Math.min(psDate.getTime() + (paintPe-psDate)*ratio, commitEnd.getTime()));
          if(expPaintStart < expFabEnd) expPaintStart = expFabEnd;
          if(expPaintEnd < expPaintStart) expPaintEnd = expPaintStart;
        } else {
          expFabStart = fabPs; expFabEnd = fabPe; expPaintStart = paintPs; expPaintEnd = paintPe;
        }
        // FAB ROW
        html += `<tr>`;
        html += `<td class="g-label" rowspan="2" style="color:#2F5496;font-size:13px">${dm.diameter}<br><span style="font-size:8px;color:#888;font-weight:400">${dm.spool_count} spools</span><div class="mini-prog"><div class="mini-prog-fill" style="width:${overallP}%"></div></div></td>`;
        html += `<td class="g-label" style="font-size:9px;color:#666">${fabLabel.split('/')[0].trim()}</td>`;
        weeks.forEach(w => {
          const inStd = fabPs<=w.end && fabPe>=w.start;
          const inExp = expFabStart<=w.end && expFabEnd>=w.start;
          const isSaved = hasExpediting && inStd && !inExp;
          const isToday = w.current;
          let content = '';
          if(inExp){ content = `<div class="g-bar g-exp-fab"></div>`;
            if(isToday) content += `<div class="g-today-line"></div><div class="g-pct">${fabP}%</div>`;
            else if(fabP >= 100 && w.end < today) content += `<div class="g-pct" style="color:#fff">\u2713</div>`;
          } else if(isSaved){ content = `<div class="g-bar g-saved"></div>`; }
          if(isToday && !inExp){
            if(fabP > 0 && fabP < 100) content = `<div class="g-bar g-exp-fab"></div><div class="g-today-line"></div><div class="g-pct">${fabP}%</div>`;
            else content += `<div class="g-today-line"></div>`;
          }
          html += `<td>${content}</td>`;
        });
        html += `</tr>`;
        // PAINT ROW
        html += `<tr><td class="g-label" style="font-size:9px;color:#666">${paintLabel.split('/')[0].trim()}</td>`;
        const isLast = dmIdx===lastDiamIdx;
        weeks.forEach(w => {
          const inStd = paintPs<=w.end && paintPe>=w.start;
          const inExp = expPaintStart<=w.end && expPaintEnd>=w.start;
          const inStdFab = fabPs<=w.end && fabPe>=w.start;
          const inExpFab = expFabStart<=w.end && expFabEnd>=w.start;
          const isSaved = hasExpediting && (inStd || inStdFab) && !inExp && !inExpFab;
          const isToday = w.current;
          const isForecastPaint = dmStarted && dmFcEnd && overallP<100 && dmFcEnd>=w.start && dmFcEnd<=w.end;
          let content = '';
          if(inExp){ content = `<div class="g-bar g-exp-paint"></div>`;
            if(isToday) content += `<div class="g-today-line"></div><div class="g-pct">${paintP}%</div>`;
            else if(paintP >= 100 && w.end < today) content += `<div class="g-pct" style="color:#fff">\u2713</div>`;
          } else if(isSaved){ content = `<div class="g-bar g-saved"></div>`; }
          if(isForecastPaint) content += `<div class="g-bar g-forecast"></div>`;
          if(isToday && !inExp){
            if(paintP > 0 && paintP < 100) content = `<div class="g-bar g-exp-paint"></div><div class="g-today-line"></div><div class="g-pct">${paintP}%</div>`;
            else content += `<div class="g-today-line"></div>`;
          }
          if(isToday && isLast) content += `<div style="position:absolute;bottom:-13px;left:50%;transform:translateX(-50%);font-size:7px;color:#e74c3c;font-weight:700;z-index:11">TODAY</div>`;
          html += `<td>${content}</td>`;
        });
        html += `</tr>`;
        html += `<tr><td colspan="${numWeeks+2}" style="height:2px;background:#f0f2f5;border:none"></td></tr>`;
      });

      html += `</tbody></table></div>
        <div class="legend">
          <span><span class="box" style="background:#4472C4"></span> ${fabLabel}</span>
          <span><span class="box" style="background:#ED7D31"></span> ${paintLabel}</span>
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
          <div style="flex:1;min-width:200px">
            <div style="font-size:12px;color:#888;margin-bottom:4px">${paintLabel} (m\u00b2/day)</div>
            <div style="display:flex;align-items:baseline;gap:8px"><span style="font-size:24px;font-weight:700;color:${actualPaint>=paintCap?'#27ae60':'#e74c3c'}">${actualPaint}</span><span style="color:#888;font-size:12px">/ ${paintCap} target</span></div>
            <div class="expected-bar" style="margin-top:4px"><div class="actual-fill" style="width:${Math.min(actualPaint/Math.max(paintCap,1)*100,100)}%;background:${actualPaint>=paintCap?'#27ae60':'#e74c3c'}"></div></div>
          </div>
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
      const arrivalDate = fcEnd ? new Date(fcEnd.getTime()+transitDays*86400000) : null;
      const commitArrival = hasExpediting ? new Date(commitEnd.getTime()+transitDays*86400000) : null;
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
