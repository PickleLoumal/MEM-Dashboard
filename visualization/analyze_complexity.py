#!/usr/bin/env python3
"""
MEM Dashboard - Enterprise Codebase Audit Report
基于 Radon 的企业级代码复杂度与质量审计生成器

特性:
- 自动化 Git/Ignore 排除
- 圈复杂度 (Cyclomatic Complexity) 深度分析
- 可维护性指数 (Maintainability Index) 热力图
- 原始代码行数 (LOC/LLOC/SLOC) 精确统计
- 企业级 HTML 仪表盘报告
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from fnmatch import fnmatch

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "visualization"

# 默认排除的目录和文件
DEFAULT_EXCLUDES = [
    "venv", ".venv", "env", ".env",
    "node_modules",
    "__pycache__", "*.pyc",
    ".git", ".svn", ".hg",
    "*.egg-info",
    "dist", "build",
    "backup", "archives",
    ".uv-cache", ".uvcache",
    "logs", "*.log",
    "*.min.js", "*.min.css",
    "migrations", "tests", "test",
    "manage.py", "wsgi.py"
]

def parse_gitignore(gitignore_path: Path) -> list:
    """解析 .gitignore 文件，返回排除模式列表"""
    patterns = []
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line.rstrip('/'))
    return patterns

def should_exclude(path: str, patterns: list) -> bool:
    """检查路径是否应该被排除"""
    path_parts = Path(path).parts
    for pattern in patterns:
        for part in path_parts:
            if fnmatch(part, pattern): return True
        if fnmatch(path, pattern) or fnmatch(path, f"**/{pattern}"): return True
    return False

def find_python_files(root_dir: Path, exclude_patterns: list) -> list:
    """递归查找所有 Python 文件"""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not should_exclude(d, exclude_patterns)]
        for file in files:
            if file.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                if not should_exclude(rel_path, exclude_patterns):
                    python_files.append(rel_path)
    return python_files

def run_radon_on_files(command: str, files: list) -> dict:
    """运行 Radon 命令"""
    if not files: return {}
    result = {}
    batch_size = 100
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        cmd = [sys.executable, "-m", "radon", command, "-j"] + batch
        if command == "cc": cmd.insert(4, "-a")
        
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        try:
            result.update(json.loads(proc.stdout) if proc.stdout else {})
        except json.JSONDecodeError: pass
    return result

def generate_enterprise_report(cc_data: dict, mi_data: dict, raw_data: dict, 
                               file_count: int, exclude_patterns: list) -> str:
    """生成企业级 HTML 审计报告"""
    
    # 1. 数据聚合与计算
    total_loc = sum(v.get('loc', 0) for v in raw_data.values() if isinstance(v, dict))
    total_lloc = sum(v.get('lloc', 0) for v in raw_data.values() if isinstance(v, dict))
    total_sloc = sum(v.get('sloc', 0) for v in raw_data.values() if isinstance(v, dict))
    total_comments = sum(v.get('comments', 0) for v in raw_data.values() if isinstance(v, dict))
    
    # 计算注释率
    comment_ratio = (total_comments / total_sloc * 100) if total_sloc > 0 else 0
    
    # 复杂度统计
    all_functions = []
    complexity_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
    
    for file_path, functions in cc_data.items():
        if isinstance(functions, list):
            for func in functions:
                if not isinstance(func, dict): continue
                rank = func.get('rank', 'A')
                complexity_dist[rank] = complexity_dist.get(rank, 0) + 1
                all_functions.append({
                    'file': file_path,
                    'name': func.get('name', ''),
                    'type': func.get('type', ''),
                    'complexity': func.get('complexity', 0),
                    'rank': rank,
                    'lineno': func.get('lineno', 0),
                })
    
    total_functions = len(all_functions)
    avg_complexity = sum(f['complexity'] for f in all_functions) / total_functions if total_functions else 0
    
    # 模块级统计
    modules = {}
    for file_path in raw_data:
        if file_path in cc_data and isinstance(raw_data[file_path], dict):
            mod = Path(file_path).parts[0]
            if mod not in modules:
                modules[mod] = {'loc': 0, 'funcs': 0, 'cc': 0, 'mi': 0, 'files': 0}
            
            modules[mod]['files'] += 1
            modules[mod]['loc'] += raw_data[file_path].get('loc', 0)
            
            funcs = cc_data.get(file_path, [])
            if isinstance(funcs, list):
                modules[mod]['funcs'] += len(funcs)
                modules[mod]['cc'] += sum(f.get('complexity', 0) for f in funcs if isinstance(f, dict))
            
            mi_score = mi_data.get(file_path, {}).get('mi', 0) if isinstance(mi_data.get(file_path), dict) else 0
            modules[mod]['mi'] += mi_score

    # 计算模块平均值
    module_list = []
    for name, stats in modules.items():
        stats['avg_cc'] = stats['cc'] / stats['funcs'] if stats['funcs'] else 0
        stats['avg_mi'] = stats['mi'] / stats['files'] if stats['files'] else 0
        module_list.append({'name': name, **stats})
    module_list.sort(key=lambda x: x['loc'], reverse=True)

    # HTML 模板 - Financial / Family Office Style
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Technical Due Diligence Report | MEM Family Office</title>
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- DataTables -->
    <link href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --primary: #0f2b46; /* Navy Blue */
            --secondary: #334155;
            --accent: #c5a059; /* Muted Gold */
            --bg-body: #f8f9fa;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #1e293b;
            --text-light: #64748b;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding-bottom: 4rem;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif;
            color: var(--primary);
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        
        /* Report Container (A4-like) */
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            padding: 4rem;
            margin-top: 2rem;
            border-top: 6px solid var(--primary);
        }}
        
        /* Header */
        .report-header {{
            border-bottom: 2px solid var(--primary);
            padding-bottom: 2rem;
            margin-bottom: 3rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .report-title {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: var(--primary);
            font-weight: 800;
        }}
        .report-subtitle {{
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: 600;
        }}
        .report-meta {{
            text-align: right;
            font-size: 0.9rem;
            color: var(--text-light);
        }}
        
        /* Section Headers */
        .section-header {{
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .section-header h2 {{
            font-size: 1.5rem;
            margin: 0;
            font-weight: 700;
        }}
        .section-number {{
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: var(--accent);
            font-size: 1.2rem;
        }}
        
        /* Executive Summary Cards */
        .exec-summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        .metric-card {{
            background: #f8fafc;
            padding: 1.5rem;
            border-left: 4px solid var(--accent);
            border-radius: 6px;
        }}
        .metric-value {{
            font-family: 'Inter', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1.1;
            letter-spacing: -0.03em;
        }}
        .metric-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-light);
            margin-top: 0.5rem;
            font-weight: 600;
        }}
        
        /* Charts */
        .chart-wrapper {{ 
            position: relative; 
            height: 300px; 
            width: 100%;
            margin-bottom: 1rem;
        }}
        
        /* Tables */
        .table {{
            width: 100%;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }}
        .table th {{
            background-color: #f1f5f9;
            color: var(--primary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            border-bottom: 2px solid var(--border-color);
        }}
        .table td {{
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}
        
        /* Risk Badges */
        .risk-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 2px;
            font-weight: 700;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .risk-low {{ background: #dcfce7; color: #14532d; }}
        .risk-med {{ background: #fef9c3; color: #713f12; }}
        .risk-high {{ background: #fee2e2; color: #7f1d1d; }}
        .risk-critical {{ background: #450a0a; color: #fff; }}
        
        /* Utility */
        .text-accent {{ color: var(--accent); }}
        .text-primary-dark {{ color: var(--primary); }}
        
        @media print {{
            .no-print {{ display: none; }}
            .report-container {{ box-shadow: none; margin: 0; padding: 0; border: none; }}
            body {{ background: #fff; }}
        }}
    </style>
</head>
<body>

    <div class="report-container">
        <!-- Header -->
        <header class="report-header">
            <div>
                <div class="report-subtitle">CONFIDENTIAL • INTERNAL USE ONLY</div>
                <h1 class="report-title">Technical Audit Report</h1>
                <div class="text-muted">Target Asset: ALFIE Python Backend</div>
            </div>
            <div class="report-meta">
                <div><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</div>
                <div><strong>Auditor:</strong> Automated System (Radon)</div>
                <div><strong>Ref:</strong> ALFIE-AUDIT-{datetime.now().strftime('%Y%m%d')}</div>
            </div>
        </header>

        <div class="no-print mb-4 text-end">
            <button class="btn btn-outline-dark btn-sm" onclick="window.print()">
                <i class="fas fa-print me-2"></i>Print / Save PDF
            </button>
        </div>

        <!-- Executive Summary -->
        <section>
            <div class="section-header">
                <span class="section-number">01</span>
                <h2>Executive Summary</h2>
            </div>
            
            <div class="exec-summary">
                <div class="metric-card">
                    <div class="metric-value">{total_loc:,}</div>
                    <div class="metric-label">Total Code Volume (LOC)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_complexity:.2f}</div>
                    <div class="metric-label">Avg. Complexity Risk</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(modules)}</div>
                    <div class="metric-label">Functional Modules</div>
                </div>
                <div class="metric-card" style="border-left-color: {'#16a34a' if comment_ratio > 10 else '#dc2626'}">
                    <div class="metric-value">{comment_ratio:.1f}%</div>
                    <div class="metric-label">Documentation Ratio</div>
                </div>
            </div>
            
            <p class="lead text-muted mb-4">
                This report provides a quantitative assessment of the codebase's structural health, 
                maintainability, and potential technical debt risks. The analysis focuses on Cyclomatic Complexity 
                and Maintainability Index (MI) to evaluate long-term viability.
            </p>
        </section>

        <!-- Structural Analysis -->
        <section>
            <div class="section-header">
                <span class="section-number">02</span>
                <h2>Structural Analysis</h2>
            </div>
            
            <div class="row">
                <div class="col-md-7">
                    <h5 class="mb-3 text-primary-dark">Module Size vs. Risk Profile</h5>
                    <p class="text-muted small mb-3">Analysis of code volume relative to complexity density per module.</p>
                    <div class="chart-wrapper">
                        <canvas id="moduleChart"></canvas>
                    </div>
                </div>
                <div class="col-md-5">
                    <h5 class="mb-3 text-primary-dark">Risk Distribution</h5>
                    <p class="text-muted small mb-3">Proportion of functions by complexity grade (A=Low Risk, F=Critical).</p>
                    <div class="chart-wrapper">
                        <canvas id="complexityPie"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- Risk Assessment -->
        <section>
            <div class="section-header">
                <span class="section-number">03</span>
                <h2>High Risk Assets (Technical Debt)</h2>
            </div>
            <p class="text-muted mb-4">
                The following components exhibit high Cyclomatic Complexity (CC), indicating complex logic 
                that may be prone to bugs and difficult to maintain. Recommended for refactoring.
            </p>
            
            <div class="table-responsive">
                <table class="table table-hover" id="hotspotsTable">
                    <thead>
                        <tr>
                            <th>Risk Grade</th>
                            <th>Complexity (CC)</th>
                            <th>Asset Name</th>
                            <th>Location</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    # Hotspots Rows
    for func in sorted(all_functions, key=lambda x: x['complexity'], reverse=True)[:30]:
        rank = func['rank']
        # Map Rank to Risk Label
        risk_label = "LOW"
        risk_class = "risk-low"
        if rank in ['C']: risk_label = "MEDIUM"; risk_class = "risk-med"
        if rank in ['D', 'E']: risk_label = "HIGH"; risk_class = "risk-high"
        if rank in ['F']: risk_label = "CRITICAL"; risk_class = "risk-critical"
        
        html += f"""
                        <tr>
                            <td><span class="risk-badge {risk_class}">{rank} - {risk_label}</span></td>
                            <td class="fw-bold">{func['complexity']}</td>
                            <td style="font-family:monospace; color:#0f2b46">{func['name']}</td>
                            <td class="text-muted small">{func['file']}:{func['lineno']}</td>
                        </tr>
"""
    html += """
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Maintainability Index -->
        <section>
            <div class="section-header">
                <span class="section-number">04</span>
                <h2>Maintainability Index (MI)</h2>
            </div>
            <div class="table-responsive">
                <table class="table" id="miTable">
                    <thead>
                        <tr>
                            <th style="width: 50%">File Asset</th>
                            <th>MI Score</th>
                            <th>Status</th>
                            <th>Volume (SLOC)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    # MI Rows
    mi_items = [(f, v) for f, v in mi_data.items() if isinstance(v, dict)]
    for file_path, info in mi_items:
        score = info.get('mi', 0)
        
        status = "Healthy"
        color = "#16a34a" # Green
        if score < 60: status = "At Risk"; color = "#ca8a04" # Yellow
        if score < 40: status = "Critical"; color = "#dc2626" # Red
        
        html += f"""
                        <tr>
                            <td style="font-family:monospace" title="{file_path}">{file_path}</td>
                            <td class="fw-bold">{score:.1f}</td>
                            <td style="color:{color}; font-weight:700">{status}</td>
                            <td>{raw_data.get(file_path, {}).get('sloc', 0)}</td>
                        </tr>
"""
    html += """
                    </tbody>
                </table>
            </div>
        </section>
        
        <footer style="margin-top: 4rem; border-top: 1px solid #eee; padding-top: 2rem; font-size: 0.8rem; color: #999; text-align: center;">
            <p>MEM Family Office • Technology Division • Generated by Automated Audit Protocol</p>
        </footer>

    </div>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
        $(document).ready(function() {
            $('#hotspotsTable').DataTable({
                pageLength: 15,
                order: [[1, 'desc']],
                dom: 't', // Simple table only
                language: { emptyTable: "No high-risk assets found." }
            });
            $('#miTable').DataTable({
                pageLength: 15,
                order: [[1, 'asc']],
                dom: 't'
            });
        });

        // Module Chart
        const ctxMod = document.getElementById('moduleChart').getContext('2d');
        new Chart(ctxMod, {
            type: 'bar',
            data: {
                labels: """ + json.dumps([m['name'] for m in module_list[:8]]) + """,
                datasets: [{
                    label: 'Code Volume (LOC)',
                    data: """ + json.dumps([m['loc'] for m in module_list[:8]]) + """,
                    backgroundColor: '#0f2b46',
                    barPercentage: 0.6,
                    yAxisID: 'y',
                }, {
                    label: 'Risk (Avg CC)',
                    data: """ + json.dumps([m['avg_cc'] for m in module_list[:8]]) + """,
                    borderColor: '#c5a059',
                    backgroundColor: '#c5a059',
                    type: 'line',
                    yAxisID: 'y1',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { usePointStyle: true } }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { position: 'left', grid: { color: '#f1f5f9' } },
                    y1: { position: 'right', grid: { display: false } }
                }
            }
        });

        // Complexity Pie
        const ctxPie = document.getElementById('complexityPie').getContext('2d');
        new Chart(ctxPie, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'Medium Risk', 'High Risk', 'Critical'],
                datasets: [{
                    data: """ + json.dumps([
                        complexity_dist['A'] + complexity_dist['B'], 
                        complexity_dist['C'],
                        complexity_dist['D'] + complexity_dist['E'], 
                        complexity_dist['F']
                    ]) + """,
                    backgroundColor: [
                        '#0f2b46', // Navy (Safe)
                        '#64748b', // Grey (Med)
                        '#c5a059', // Gold (High)
                        '#991b1b'  // Red (Critical)
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { position: 'right', labels: { usePointStyle: true, font: { size: 11 } } }
                }
            }
        });
    </script>
</body>
</html>
"""
    return html

def main():
    print("=" * 60)
    print("🚀 Starting Enterprise Code Audit")
    print("=" * 60)
    
    gitignore_path = PROJECT_ROOT / ".gitignore"
    excludes = parse_gitignore(gitignore_path) + DEFAULT_EXCLUDES
    excludes = list(set(excludes))
    
    print(f"📋 Loaded {len(excludes)} exclusion patterns")
    
    python_files = find_python_files(PROJECT_ROOT, excludes)
    print(f"🔎 Found {len(python_files)} Python files to analyze")
    
    if not python_files:
        print("❌ No files found.")
        return

    print("📊 Analyzing Cyclomatic Complexity...")
    cc_data = run_radon_on_files("cc", python_files)
    
    print("📈 Analyzing Maintainability Index...")
    mi_data = run_radon_on_files("mi", python_files)
    
    print("📝 Analyzing Raw Metrics (LOC)...")
    raw_data = run_radon_on_files("raw", python_files)
    
    html_content = generate_enterprise_report(cc_data, mi_data, raw_data, len(python_files), excludes)
    html_path = OUTPUT_DIR / "audit_report.html"
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("\n" + "=" * 60)
    print(f"✅ AUDIT COMPLETE")
    print(f"📄 Report: file://{html_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
