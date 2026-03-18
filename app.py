#!/usr/bin/env python3
"""
Charlie Tracker — Spool Production Tracking System
Bilingual EN/CN web app. Works in China and internationally.
Supports PostgreSQL (Render) and SQLite (local).
"""

import os
import sys
import json
import argparse
from datetime import datetime, date
from contextlib import contextmanager

from flask import (
    Flask, render_template_string, request, jsonify,
    redirect, url_for, send_file, g
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'charlie-tracker-dev-key-2026')

DATABASE_URL = os.environ.get('DATABASE_URL', '')
USE_PG = DATABASE_URL.startswith('postgres')

# ── Production Steps (ITP) ────────────────────────────────────────────────────

PRODUCTION_STEPS = [
    (1,  "Material Receiving & Traceability",       "来料检验及可追溯性",              5),
    (2,  "Documentation Review (WPS/PQR/ITP)",      "文件审查（WPS/PQR/ITP）",        3),
    (3,  "Pipe Cutting — Dimensional Check",        "管道切割 — 尺寸检验",            8),
    (4,  "End Preparation / Bevelling",             "管口准备 / 坡口加工",            5),
    (5,  "Fit-Up & Assembly Inspection",            "组对及装配检验",                 10),
    (6,  "Production Welding as per WPS",           "按WPS生产焊接",                 15),
    (7,  "Visual Inspection (VT) — 100%",           "目视检验VT（全检）",              8),
    (8,  "Radiographic Test (RT) — 100%",           "射线检测RT（全检）★停止点",       10),
    (9,  "Magnetic Particle (MT) — 100%",           "磁粉检测MT（全检）",              5),
    (10, "Cleaning Prior to Painting",              "涂装前清洁处理",                  3),
    (11, "Surface Preparation — Blasting",          "表面处理 — 喷砂",                8),
    (12, "Painting Application",                    "涂装施工（底漆/中间漆/面漆）",     8),
    (13, "Coating Inspection — DFT",                "涂层检验 — 膜厚及附着力",         4),
    (14, "Dimensional Inspection & Marking",        "尺寸检验及标识",                  5),
    (15, "Final Inspection — Released",             "最终检验 — 发货放行 ★见证",       3),
]

# ── Database Layer ────────────────────────────────────────────────────────────

def get_db():
    if 'db' not in g:
        if USE_PG:
            import psycopg2
            import psycopg2.extras
            url = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            g.db = psycopg2.connect(url)
            g.db.autocommit = False
            g.db_type = 'pg'
        else:
            import sqlite3
            db_path = os.environ.get('SQLITE_PATH', 'tracker.db')
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row
            g.db_type = 'sqlite'
    return g.db


def db_execute(query, params=None):
    """Execute query, handling PG vs SQLite differences."""
    db = get_db()
    if g.db_type == 'pg':
        import psycopg2.extras
        # Convert ? placeholders to %s for PG
        query = query.replace('?', '%s')
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params or ())
        return cur
    else:
        return db.execute(query, params or ())


def db_fetchall(query, params=None):
    cur = db_execute(query, params)
    rows = cur.fetchall()
    if g.db_type == 'pg':
        return rows  # Already dicts
    return [dict(r) for r in rows]


def db_fetchone(query, params=None):
    cur = db_execute(query, params)
    row = cur.fetchone()
    if row and g.db_type == 'pg':
        return row  # Already dict
    return dict(row) if row else None


def db_commit():
    db = get_db()
    db.commit()


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()


def init_db():
    """Create tables if they don't exist."""
    if USE_PG:
        import psycopg2
        url = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(url)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS spools (
                id SERIAL PRIMARY KEY,
                spool_id TEXT UNIQUE NOT NULL,
                spool_full TEXT DEFAULT '',
                iso_no TEXT DEFAULT '',
                marking TEXT DEFAULT '',
                mk_number TEXT DEFAULT '',
                main_diameter TEXT DEFAULT '',
                line TEXT DEFAULT '',
                sequence INTEGER DEFAULT 0,
                project TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS progress (
                id SERIAL PRIMARY KEY,
                spool_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_by TEXT DEFAULT '',
                completed_at TIMESTAMP,
                remarks TEXT DEFAULT '',
                UNIQUE(spool_id, step_number)
            );
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                spool_id TEXT NOT NULL,
                step_number INTEGER,
                action TEXT NOT NULL,
                operator TEXT DEFAULT '',
                timestamp TIMESTAMP DEFAULT NOW(),
                details TEXT DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS idx_progress_spool ON progress(spool_id);
            CREATE INDEX IF NOT EXISTS idx_activity_spool ON activity_log(spool_id);
        """)
        conn.close()
    else:
        import sqlite3
        db_path = os.environ.get('SQLITE_PATH', 'tracker.db')
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS spools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spool_id TEXT UNIQUE NOT NULL,
                spool_full TEXT DEFAULT '',
                iso_no TEXT DEFAULT '',
                marking TEXT DEFAULT '',
                mk_number TEXT DEFAULT '',
                main_diameter TEXT DEFAULT '',
                line TEXT DEFAULT '',
                sequence INTEGER DEFAULT 0,
                project TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spool_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_by TEXT DEFAULT '',
                completed_at TEXT,
                remarks TEXT DEFAULT '',
                UNIQUE(spool_id, step_number)
            );
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spool_id TEXT NOT NULL,
                step_number INTEGER,
                action TEXT NOT NULL,
                operator TEXT DEFAULT '',
                timestamp TEXT DEFAULT (datetime('now')),
                details TEXT DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS idx_progress_spool ON progress(spool_id);
            CREATE INDEX IF NOT EXISTS idx_activity_spool ON activity_log(spool_id);
        """)
        conn.close()


# ── Spool Import ──────────────────────────────────────────────────────────────

def import_spools_from_json(data):
    """Import spools from JSON list of dicts."""
    count = 0
    with app.app_context():
        db = get_db()
        for s in data:
            try:
                if USE_PG:
                    db_execute("""
                        INSERT INTO spools (spool_id, spool_full, iso_no, marking, mk_number, main_diameter, line, sequence, project)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (spool_id) DO NOTHING
                    """, (s['spool_id'], s.get('spool_full',''), s.get('iso_no',''),
                          s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''),
                          s.get('line',''), s.get('sequence',0), s.get('project','')))
                else:
                    db_execute("""
                        INSERT OR IGNORE INTO spools (spool_id, spool_full, iso_no, marking, mk_number, main_diameter, line, sequence, project)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (s['spool_id'], s.get('spool_full',''), s.get('iso_no',''),
                          s.get('marking',''), s.get('mk_number',''), s.get('main_diameter',''),
                          s.get('line',''), s.get('sequence',0), s.get('project','')))

                for step_num, _, _, _ in PRODUCTION_STEPS:
                    if USE_PG:
                        db_execute("""
                            INSERT INTO progress (spool_id, step_number, completed)
                            VALUES (?, ?, 0) ON CONFLICT (spool_id, step_number) DO NOTHING
                        """, (s['spool_id'], step_num))
                    else:
                        db_execute("""
                            INSERT OR IGNORE INTO progress (spool_id, step_number, completed)
                            VALUES (?, ?, 0)
                        """, (s['spool_id'], step_num))
                count += 1
            except Exception as e:
                print(f"  Error importing {s.get('spool_id','?')}: {e}")

        db_commit()
    return count


# ── Helper Functions ──────────────────────────────────────────────────────────

def get_spool_progress(spool_id):
    rows = db_fetchall(
        "SELECT step_number, completed FROM progress WHERE spool_id = ?", (spool_id,)
    )
    weight_map = {s[0]: s[3] for s in PRODUCTION_STEPS}
    total_weight = sum(weight_map.values())
    completed_weight = sum(weight_map.get(r['step_number'], 0) for r in rows if r['completed'])
    return (completed_weight / total_weight * 100) if total_weight else 0.0


def get_dashboard_stats():
    spools = db_fetchall("SELECT * FROM spools ORDER BY sequence")
    stats = {
        'total_spools': len(spools), 'completed': 0, 'in_progress': 0,
        'not_started': 0, 'overall_pct': 0.0,
        'by_diameter': {}, 'by_line': {},
    }
    total_pct = 0
    for s in spools:
        pct = get_spool_progress(s['spool_id'])
        total_pct += pct
        if pct >= 100: stats['completed'] += 1
        elif pct > 0: stats['in_progress'] += 1
        else: stats['not_started'] += 1

        diam = s['main_diameter'] or '?'
        if diam not in stats['by_diameter']:
            stats['by_diameter'][diam] = {'total': 0, 'pct_sum': 0}
        stats['by_diameter'][diam]['total'] += 1
        stats['by_diameter'][diam]['pct_sum'] += pct

        line = s['line'] or '?'
        if line not in stats['by_line']:
            stats['by_line'][line] = {'total': 0, 'pct_sum': 0}
        stats['by_line'][line]['total'] += 1
        stats['by_line'][line]['pct_sum'] += pct

    if spools:
        stats['overall_pct'] = round(total_pct / len(spools), 1)
    for d in stats['by_diameter'].values():
        d['avg_pct'] = round(d['pct_sum'] / d['total'], 1) if d['total'] else 0
    for l in stats['by_line'].values():
        l['avg_pct'] = round(l['pct_sum'] / l['total'], 1) if l['total'] else 0

    activity = db_fetchall("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 20")
    stats['recent_activity'] = activity
    return stats


# ── API Routes ────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(get_dashboard_stats())

@app.route('/api/spools')
def api_spools():
    spools = db_fetchall("SELECT * FROM spools ORDER BY sequence")
    result = []
    for s in spools:
        pct = get_spool_progress(s['spool_id'])
        steps = db_fetchall(
            "SELECT step_number, completed, completed_by, completed_at, remarks "
            "FROM progress WHERE spool_id = ? ORDER BY step_number", (s['spool_id'],)
        )
        # Convert datetime objects to strings for JSON
        for st in steps:
            if st.get('completed_at') and not isinstance(st['completed_at'], str):
                st['completed_at'] = str(st['completed_at'])
        result.append({'spool': s, 'progress_pct': round(pct, 1), 'steps': steps})
    return jsonify(result)

@app.route('/api/spool/<spool_id>')
def api_spool_detail(spool_id):
    spool = db_fetchone("SELECT * FROM spools WHERE spool_id = ?", (spool_id,))
    if not spool:
        return jsonify({'error': 'Spool not found'}), 404
    steps = db_fetchall(
        "SELECT * FROM progress WHERE spool_id = ? ORDER BY step_number", (spool_id,)
    )
    for st in steps:
        if st.get('completed_at') and not isinstance(st['completed_at'], str):
            st['completed_at'] = str(st['completed_at'])
    pct = get_spool_progress(spool_id)
    activity = db_fetchall(
        "SELECT * FROM activity_log WHERE spool_id = ? ORDER BY timestamp DESC LIMIT 10", (spool_id,)
    )
    for a in activity:
        if a.get('timestamp') and not isinstance(a['timestamp'], str):
            a['timestamp'] = str(a['timestamp'])
    return jsonify({
        'spool': spool, 'progress_pct': round(pct, 1), 'steps': steps,
        'activity': activity,
        'step_definitions': [
            {'number': s[0], 'name_en': s[1], 'name_cn': s[2], 'weight': s[3]}
            for s in PRODUCTION_STEPS
        ],
    })

@app.route('/api/spool/<spool_id>/step/<int:step_number>', methods=['POST'])
def api_update_step(spool_id, step_number):
    data = request.get_json() or {}
    completed = 1 if data.get('completed', False) else 0
    operator = data.get('operator', '')
    remarks = data.get('remarks', '')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if USE_PG:
        db_execute("""
            INSERT INTO progress (spool_id, step_number, completed, completed_by, completed_at, remarks)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (spool_id, step_number) DO UPDATE SET
                completed = EXCLUDED.completed,
                completed_by = EXCLUDED.completed_by,
                completed_at = CASE WHEN EXCLUDED.completed = 1 THEN EXCLUDED.completed_at ELSE NULL END,
                remarks = EXCLUDED.remarks
        """, (spool_id, step_number, completed, operator, now if completed else None, remarks))
    else:
        db_execute("""
            INSERT INTO progress (spool_id, step_number, completed, completed_by, completed_at, remarks)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(spool_id, step_number) DO UPDATE SET
                completed = excluded.completed,
                completed_by = excluded.completed_by,
                completed_at = CASE WHEN excluded.completed = 1 THEN excluded.completed_at ELSE NULL END,
                remarks = excluded.remarks
        """, (spool_id, step_number, completed, operator, now if completed else None, remarks))

    step_name = next((s[1] for s in PRODUCTION_STEPS if s[0] == step_number), f"Step {step_number}")
    action = "completed" if completed else "unchecked"
    db_execute("""
        INSERT INTO activity_log (spool_id, step_number, action, operator, details)
        VALUES (?, ?, ?, ?, ?)
    """.replace('?' if USE_PG else '!NEVER!', '%s'),
        (spool_id, step_number, action, operator, f"{step_name}: {action} by {operator}"))

    db_commit()
    pct = get_spool_progress(spool_id)
    return jsonify({'ok': True, 'progress_pct': round(pct, 1)})

@app.route('/api/import', methods=['POST'])
def api_import():
    """Import spools via JSON API (for remote initialization)."""
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Expected JSON array of spool objects'}), 400
    count = import_spools_from_json(data)
    return jsonify({'ok': True, 'imported': count})

@app.route('/api/export')
def api_export():
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    import tempfile

    spools = db_fetchall("SELECT * FROM spools ORDER BY sequence")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Production Progress"

    headers = ['#', 'Spool', 'Diameter', 'Line', 'Progress %']
    for s in PRODUCTION_STEPS:
        headers.append(f"S{s[0]}")
    hfont = Font(bold=True, size=9, color='FFFFFF')
    hfill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    for col, h in enumerate(headers, 1):
        cell = ws.cell(1, col, h)
        cell.font = hfont
        cell.fill = hfill
        cell.alignment = Alignment(horizontal='center', wrap_text=True)

    for i, s in enumerate(spools, 2):
        pct = get_spool_progress(s['spool_id'])
        steps = db_fetchall(
            "SELECT step_number, completed FROM progress WHERE spool_id = ?", (s['spool_id'],)
        )
        step_map = {st['step_number']: st['completed'] for st in steps}

        ws.cell(i, 1, i - 1)
        ws.cell(i, 2, s['spool_id'])
        ws.cell(i, 3, s['main_diameter'])
        ws.cell(i, 4, s['line'])
        ws.cell(i, 5, round(pct, 1))
        for j, step_def in enumerate(PRODUCTION_STEPS):
            col = 6 + j
            done = step_map.get(step_def[0], 0)
            ws.cell(i, col, '✓' if done else '')
            if done:
                ws.cell(i, col).fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')

    ws.column_dimensions['B'].width = 15
    ws.freeze_panes = 'A2'

    tmp = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    wb.save(tmp.name)
    return send_file(tmp.name, as_attachment=True,
                     download_name=f"production_progress_{date.today().strftime('%Y%m%d')}.xlsx")

@app.route('/spool/<spool_id>')
def spool_detail_page(spool_id):
    return render_template_string(SPOOL_DETAIL_HTML, spool_id=spool_id)


# ── HTML Templates ────────────────────────────────────────────────────────────

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ENERXON Tracker — Production Progress / 生产进度</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#333}
.header{background:linear-gradient(135deg,#2F5496,#1a3a6e);color:#fff;padding:16px 20px}
.header h1{font-size:20px}.header .sub{font-size:12px;opacity:.8;margin-top:4px}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;padding:16px}
.stat-card{background:#fff;border-radius:10px;padding:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.stat-card .value{font-size:28px;font-weight:700;color:#2F5496}
.stat-card .label{font-size:11px;color:#888;margin-top:4px}
.pbar-bg{background:#e8e8e8;border-radius:8px;height:12px;overflow:hidden}
.pbar-fill{height:100%;border-radius:8px;transition:width .5s}
.section{padding:0 16px 16px}.section h2{font-size:16px;color:#2F5496;margin:16px 0 8px}
.toolbar{display:flex;gap:8px;padding:8px 16px;flex-wrap:wrap}
.toolbar input,.toolbar select{padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px}
.toolbar input{flex:1;min-width:150px}
.btn{background:#2F5496;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px;text-decoration:none;display:inline-block}
.btn:hover{background:#1a3a6e}
.spool-list{display:grid;gap:8px}
.spool-row{background:#fff;border-radius:8px;padding:12px 16px;display:flex;align-items:center;gap:12px;box-shadow:0 1px 2px rgba(0,0,0,.05);cursor:pointer;transition:transform .1s}
.spool-row:active{transform:scale(.99)}
.spool-row .info{flex:1;min-width:0}.spool-row .name{font-weight:600;font-size:14px}.spool-row .meta{font-size:11px;color:#888}
.spool-row .pct{font-size:18px;font-weight:700;min-width:55px;text-align:right}
.spool-row .bar{width:80px;min-width:80px}
.line-badge{display:inline-block;width:22px;height:22px;border-radius:50%;color:#fff;text-align:center;line-height:22px;font-size:11px;font-weight:700}
.line-A{background:#2d8a4e}.line-B{background:#2F5496}.line-C{background:#c0392b}
.pct-green{color:#27ae60}.pct-yellow{color:#f39c12}.pct-red{color:#e74c3c}.pct-blue{color:#2F5496}
.diam-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px}
.diam-card{background:#fff;border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.diam-card .d{font-size:20px;font-weight:700;color:#2F5496}.diam-card .p{font-size:13px;margin-top:4px}
.activity{padding:0 16px 16px}
.activity-item{font-size:12px;padding:6px 0;border-bottom:1px solid #f0f0f0;color:#666}
.activity-item .time{color:#aaa;font-size:11px}
@media(max-width:600px){.spool-row .bar{display:none}.stats-grid{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="header">
  <h1>ENERXON Production Tracker</h1>
  <div class="sub">生产进度追踪系统 — <span id="pn"></span></div>
</div>
<div class="stats-grid" id="stats"></div>
<div class="section"><h2>By Diameter / 按管径</h2><div class="diam-grid" id="diam-stats"></div></div>
<div class="toolbar">
  <input type="text" id="search" placeholder="Search spool / 搜索管段..." oninput="filterSpools()">
  <select id="fl" onchange="filterSpools()"><option value="">All Lines</option><option value="A">Line A</option><option value="B">Line B</option><option value="C">Line C</option></select>
  <select id="fs" onchange="filterSpools()"><option value="">All Status</option><option value="done">Done ✓</option><option value="wip">In Progress</option><option value="todo">Not Started</option></select>
  <a class="btn" href="/api/export">📥 Export Excel</a>
</div>
<div class="section"><div class="spool-list" id="spool-list"></div></div>
<div class="activity" id="activity-section"></div>
<script>
let allSpools=[];
async function load(){
  const[sr,spr]=await Promise.all([fetch('/api/dashboard'),fetch('/api/spools')]);
  const stats=await sr.json();allSpools=await spr.json();
  const proj=allSpools[0]?.spool?.project||'';
  document.getElementById('pn').textContent=proj;
  document.getElementById('stats').innerHTML=`
    <div class="stat-card"><div class="value">${stats.total_spools}</div><div class="label">Total Spools / 总管段</div></div>
    <div class="stat-card"><div class="value pct-blue">${stats.overall_pct}%</div><div class="label">Overall / 总进度</div>
      <div class="pbar-bg" style="margin-top:8px"><div class="pbar-fill" style="width:${stats.overall_pct}%;background:#2F5496"></div></div></div>
    <div class="stat-card"><div class="value pct-green">${stats.completed}</div><div class="label">Completed / 已完成</div></div>
    <div class="stat-card"><div class="value pct-yellow">${stats.in_progress}</div><div class="label">In Progress / 进行中</div></div>
    <div class="stat-card"><div class="value pct-red">${stats.not_started}</div><div class="label">Not Started / 未开始</div></div>`;
  const diams=Object.entries(stats.by_diameter).sort((a,b)=>(parseInt(b[0])||0)-(parseInt(a[0])||0));
  document.getElementById('diam-stats').innerHTML=diams.map(([d,v])=>`
    <div class="diam-card"><div class="d">${d}</div><div class="p">${v.total} spools</div>
      <div class="pbar-bg" style="margin-top:6px"><div class="pbar-fill" style="width:${v.avg_pct}%;background:${v.avg_pct>=100?'#27ae60':'#2F5496'}"></div></div>
      <div style="font-size:12px;margin-top:4px;font-weight:600">${v.avg_pct}%</div></div>`).join('');
  renderSpools(allSpools);
  if(stats.recent_activity&&stats.recent_activity.length){
    document.getElementById('activity-section').innerHTML='<h2 style="font-size:16px;color:#2F5496;margin:8px 0">Recent Activity / 最近动态</h2>'+
      stats.recent_activity.slice(0,10).map(a=>`<div class="activity-item"><strong>${a.spool_id}</strong> — ${a.details||a.action} <span class="time">${a.timestamp||''}</span></div>`).join('');
  }
}
function renderSpools(spools){
  document.getElementById('spool-list').innerHTML=spools.map(s=>{
    const p=s.progress_pct,cls=p>=100?'pct-green':p>0?'pct-yellow':'pct-red',bg=p>=100?'#27ae60':p>0?'#f39c12':'#e8e8e8',l=s.spool.line||'?';
    return`<div class="spool-row" onclick="location.href='/spool/${s.spool.spool_id}'" data-l="${l}" data-p="${p}" data-n="${s.spool.spool_id}">
      <span class="line-badge line-${l}">${l}</span>
      <div class="info"><div class="name">${s.spool.spool_id}</div><div class="meta">${s.spool.main_diameter||''} · ${s.spool.iso_no||''}</div></div>
      <div class="bar"><div class="pbar-bg"><div class="pbar-fill" style="width:${p}%;background:${bg}"></div></div></div>
      <div class="pct ${cls}">${p}%</div></div>`;}).join('');
}
function filterSpools(){
  const q=document.getElementById('search').value.toLowerCase(),line=document.getElementById('fl').value,st=document.getElementById('fs').value;
  renderSpools(allSpools.filter(s=>{
    if(q&&!s.spool.spool_id.toLowerCase().includes(q)&&!(s.spool.iso_no||'').toLowerCase().includes(q))return false;
    if(line&&s.spool.line!==line)return false;
    if(st==='done'&&s.progress_pct<100)return false;
    if(st==='wip'&&(s.progress_pct<=0||s.progress_pct>=100))return false;
    if(st==='todo'&&s.progress_pct>0)return false;
    return true;
  }));
}
load();setInterval(load,30000);
</script>
</body></html>"""

SPOOL_DETAIL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ spool_id }} — Checklist / 检查清单</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#333}
.header{background:linear-gradient(135deg,#2F5496,#1a3a6e);color:#fff;padding:16px 20px}
.header h1{font-size:20px}.header .sub{font-size:12px;opacity:.8}
.back{color:#fff;text-decoration:none;font-size:13px;opacity:.8}.back:hover{opacity:1}
.info-bar{background:#fff;padding:12px 16px;display:flex;flex-wrap:wrap;gap:16px;align-items:center;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.info-item{font-size:12px}.info-item .lb{color:#888}.info-item .vl{font-weight:600}
.prog-ring{text-align:center;padding:20px}
.prog-ring .big{font-size:48px;font-weight:700;color:#2F5496}
.prog-ring .lbl{font-size:13px;color:#888}
.pbar-bg{background:#e8e8e8;border-radius:8px;height:16px;margin:8px 16px;overflow:hidden}
.pbar-fill{height:100%;border-radius:8px;transition:width .5s;background:#2F5496}
.op-input{padding:8px 16px}
.op-input input{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px}
.checklist{padding:8px 16px 80px}
.step{background:#fff;border-radius:10px;margin-bottom:8px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.step.done{border-left:4px solid #27ae60}.step.pending{border-left:4px solid #e8e8e8}
.step-h{display:flex;align-items:center;padding:14px 16px;gap:12px;cursor:pointer}
.step-h .num{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0}
.step.done .num{background:#27ae60;color:#fff}.step.pending .num{background:#e8e8e8;color:#888}
.step-h .text{flex:1}.step-h .en{font-size:13px;font-weight:600}.step-h .cn{font-size:11px;color:#888}
.step-h .chk{font-size:24px}
.step-meta{padding:0 16px 12px 56px;font-size:11px;color:#888}
.step-rem{padding:4px 16px 12px 56px}
.step-rem input{width:100%;padding:6px 10px;border:1px solid #ddd;border-radius:6px;font-size:12px}
.wbadge{font-size:10px;background:#f0f2f5;padding:2px 6px;border-radius:4px;color:#888}
.line-badge{display:inline-block;width:24px;height:24px;border-radius:50%;color:#fff;text-align:center;line-height:24px;font-size:12px;font-weight:700}
.line-A{background:#2d8a4e}.line-B{background:#2F5496}.line-C{background:#c0392b}
</style>
</head>
<body>
<div class="header">
  <a class="back" href="/">← Dashboard / 返回</a>
  <h1 id="st">{{ spool_id }}</h1>
  <div class="sub" id="ss"></div>
</div>
<div class="info-bar" id="ib"></div>
<div class="prog-ring"><div class="big" id="bp">0%</div><div class="lbl">Production Progress / 生产进度</div></div>
<div class="pbar-bg"><div class="pbar-fill" id="mb" style="width:0%"></div></div>
<div class="op-input"><input type="text" id="op" placeholder="Your name / 你的姓名" value=""></div>
<div class="checklist" id="cl"></div>
<script>
const SID='{{spool_id}}';let D=null;
async function load(){
  const r=await fetch(`/api/spool/${SID}`);D=await r.json();render();
}
function render(){
  const s=D.spool,p=D.progress_pct;
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
    <div class="info-item"><span class="lb">Seq:</span> <span class="vl">#${s.sequence}</span></div>`;
  const sm={};D.steps.forEach(x=>{sm[x.step_number]=x});
  document.getElementById('cl').innerHTML=D.step_definitions.map(d=>{
    const st=sm[d.number]||{},dn=st.completed?true:false;
    return`<div class="step ${dn?'done':'pending'}" id="s${d.number}">
      <div class="step-h" onclick="tog(${d.number},${dn?'false':'true'})">
        <div class="num">${d.number}</div>
        <div class="text"><div class="en">${d.name_en} <span class="wbadge">${d.weight}%</span></div><div class="cn">${d.name_cn}</div></div>
        <div class="chk">${dn?'✅':'⬜'}</div>
      </div>
      ${dn&&st.completed_by?`<div class="step-meta">✓ ${st.completed_by} · ${st.completed_at||''}</div>`:''}
      <div class="step-rem"><input type="text" placeholder="Remarks / 备注" value="${st.remarks||''}" onchange="rem(${d.number},this.value)" onclick="event.stopPropagation()"></div>
    </div>`;}).join('');
}
async function tog(n,c){
  const op=document.getElementById('op').value||'Unknown';
  const el=document.getElementById('s'+n),ri=el.querySelector('.step-rem input');
  await fetch(`/api/spool/${SID}/step/${n}`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({completed:c,operator:op,remarks:ri?ri.value:''})});
  await load();
}
async function rem(n,v){
  const op=document.getElementById('op').value||'';
  const sm={};D.steps.forEach(x=>{sm[x.step_number]=x});const st=sm[n]||{};
  await fetch(`/api/spool/${SID}/step/${n}`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({completed:st.completed?true:false,operator:st.completed_by||op,remarks:v})});
}
load();
</script>
</body></html>"""


# ── Entry Point ───────────────────────────────────────────────────────────────

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
