# PM-39 Prompt — Public Factor-Evaluation Page Deployment Availability Debug

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository and, if available, on the deployment server.

This task follows PM-38B:

- local factor-evaluation page QA passed;
- entrypoint docs and runbook were aligned;
- however the public URL is not accessible:

```text
https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html
```

Before factor interpretation, we must verify public page delivery. A factor-evaluation page that only exists locally but cannot be opened from the public URL is not a complete research delivery artifact.

## 0. PM objective

Diagnose and repair public availability of the factor-evaluation page.

This PM should answer:

1. Does the local HTML file exist and pass completeness QA?
2. Is the public URL path correct?
3. Is the server serving `reports/site/factor-library/` at `/momentum/factor-library/`?
4. Is Apache / nginx / reverse proxy configuration correct?
5. Are file permissions, path aliases, TLS ports, or DNS/reverse-proxy settings blocking access?
6. Can the public URL return HTTP 200 for `factor-evaluation.html`?
7. Can this deployment check be repeated after future page rebuilds?

This is a deployment / serving / availability task. It is not factor interpretation.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify expected_direction.

Do **not** modify factor_values.

Do **not** modify diagnostics outputs unless page rebuild is strictly necessary.

Do **not** modify signal panel construction.

Do **not** enter factor interpretation or direction semantics review.

Do **not** touch live trading / strategy / broker / exchange execution code.

Do **not** run a full factor refresh.

## 2. Required repository files to inspect first

Read:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/REGENERATION_CONTRACT.md
docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md
docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md
docs/factor_library/audits/pm38b_entrypoint_doc_alignment_runbook_repair.md
reports/site/factor-library/index.html
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/_archive/deployment-model.html
scripts/check_factor_evaluation_page_completeness.py
```

The archived deployment model says the intended model is:

```text
site directory: reports/site/factor-library/
route: Alias /momentum/factor-library/ -> project directory
ports: 443 + 24443
no publish script required
```

Verify whether this is still true on the actual server.

## 3. Required local checks

Run from repository root:

```bash
pwd
ls -lh reports/site/factor-library/index.html
ls -lh reports/site/factor-library/factor-evaluation.html
python scripts/check_factor_evaluation_page_completeness.py
python - <<'PY'
from pathlib import Path
p = Path('reports/site/factor-library/factor-evaluation.html')
print('exists', p.exists())
print('size_bytes', p.stat().st_size if p.exists() else None)
print('contains Unified Factor Profile', 'Unified Factor Profile' in p.read_text(encoding='utf-8', errors='ignore') if p.exists() else None)
PY
```

If local QA fails, fix local page generation before deployment debugging.

## 4. Required public / server checks

Run these checks on the server where the domain is served.

### 4.1 Public URL checks

```bash
curl -I https://jp.jerrypsy.top/momentum/factor-library/
curl -I https://jp.jerrypsy.top/momentum/factor-library/index.html
curl -I https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html
curl -L -I https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html
```

Capture status code, redirects, content-type, and content-length.

### 4.2 Local server checks

Try both normal TLS and the documented 24443 port if configured:

```bash
curl -k -I https://127.0.0.1/momentum/factor-library/factor-evaluation.html || true
curl -k -I https://localhost/momentum/factor-library/factor-evaluation.html || true
curl -k -I https://127.0.0.1:24443/momentum/factor-library/factor-evaluation.html || true
curl -k -I https://localhost:24443/momentum/factor-library/factor-evaluation.html || true
```

If Apache listens on HTTP locally:

```bash
curl -I http://127.0.0.1/momentum/factor-library/factor-evaluation.html || true
```

### 4.3 Apache / nginx configuration checks

Detect web server:

```bash
ps aux | grep -E 'apache|httpd|nginx' | grep -v grep || true
```

If Apache:

```bash
apache2ctl -S || apachectl -S || httpd -S || true
grep -R "momentum/factor-library" /etc/apache2 /etc/httpd 2>/dev/null || true
grep -R "reports/site/factor-library" /etc/apache2 /etc/httpd 2>/dev/null || true
```

If nginx:

```bash
nginx -T 2>/dev/null | grep -n "momentum/factor-library\|reports/site/factor-library" || true
```

Check that the alias/location points to the current repository path and not an older checkout.

### 4.4 Filesystem and permissions

```bash
readlink -f reports/site/factor-library
readlink -f reports/site/factor-library/factor-evaluation.html
namei -l reports/site/factor-library/factor-evaluation.html || true
stat reports/site/factor-library/factor-evaluation.html
```

If Apache user is `www-data` or `apache`, verify it can read the file and traverse parent dirs.

### 4.5 Logs

```bash
tail -n 100 /var/log/apache2/error.log 2>/dev/null || true
tail -n 100 /var/log/apache2/access.log 2>/dev/null || true
tail -n 100 /var/log/httpd/error_log 2>/dev/null || true
tail -n 100 /var/log/httpd/access_log 2>/dev/null || true
tail -n 100 /var/log/nginx/error.log 2>/dev/null || true
tail -n 100 /var/log/nginx/access.log 2>/dev/null || true
```

Look for 404, 403, permission denied, alias mismatch, TLS/vhost mismatch, or upstream/reverse-proxy errors.

## 5. Required repair actions

Apply the minimal repair needed.

Possible repairs include:

- fix Apache Alias / Directory block;
- fix nginx location/root/alias;
- update symlink or deployment path to current repo;
- fix permissions on `reports/site/factor-library/` and parent directories;
- regenerate page if file missing;
- update factor-library index if it links stale counts or stale paths;
- add a small deployment health check script.

Do **not** touch factor computation or diagnostics unless page file is missing and must be regenerated.

## 6. Required optional script

If feasible, create:

```text
scripts/check_factor_library_public_url.py
```

It should check:

```text
https://jp.jerrypsy.top/momentum/factor-library/
https://jp.jerrypsy.top/momentum/factor-library/index.html
https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html
```

And output:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_public_url_check.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_public_url_check.json
```

If external network access from server is unavailable, document this and rely on local curl / reverse proxy checks.

## 7. Required docs update

Create or update:

```text
docs/factor_library/DEPLOYMENT_TROUBLESHOOTING.md
```

It should include:

- expected local file path;
- expected public URL;
- expected Apache/nginx route;
- common failure modes:
  - 404 alias mismatch;
  - 403 permissions;
  - DNS/TLS/vhost mismatch;
  - stale checkout path;
  - page generated but not served;
  - file too large or server timeout;
- commands to diagnose;
- commands to verify after repair;
- warning not to mix factor-library serving with unrelated report publish scripts.

Add this doc to `START_HERE.md` / `CONTROL_CENTER` only if low-risk and clearly useful.

## 8. Required audit

Create:

```text
docs/factor_library/audits/pm39_public_factor_page_deployment_availability.md
```

Audit must include:

1. Summary verdict:
   - `PUBLIC_FACTOR_PAGE_DEPLOYMENT_PASS`
   - `PUBLIC_FACTOR_PAGE_DEPLOYMENT_PASS_WITH_LIMITATIONS`
   - `PUBLIC_FACTOR_PAGE_DEPLOYMENT_BLOCKED`
2. Why PM-39 was required before factor interpretation.
3. Local file checks.
4. Page completeness QA result.
5. Public URL check before repair.
6. Server local URL check.
7. Web server configuration findings.
8. Filesystem / permission findings.
9. Logs summary.
10. Repair applied.
11. Public URL check after repair.
12. Confirmation whether `https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html` returns HTTP 200.
13. Files changed.
14. Confirmation no factors / formulas / factor_values / signal / diagnostics were changed.
15. Remaining limitations.
16. Recommended next PM: PM-40 post-intake factor interpretation and direction-semantics review.

## 9. Allowed files to change

Allowed scripts/docs:

```text
scripts/check_factor_library_public_url.py
docs/factor_library/DEPLOYMENT_TROUBLESHOOTING.md
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/audits/pm39_public_factor_page_deployment_availability.md
```

Allowed page files only if needed:

```text
reports/site/factor-library/index.html
reports/site/factor-library/factor-evaluation.html
```

Allowed diagnostic output:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_public_url_check.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_library_public_url_check.json
```

Server config files may need to be changed outside git. If changed outside git, document exact path and diff/summary in the audit.

Do not modify:

```text
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_*.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_*.json
reports/site/factors/*
reports/site/paper/*
src/momentum/strategies/*
```

## 10. Stop conditions

Stop and report if:

- local HTML file is missing and cannot be regenerated safely;
- page completeness QA fails and cannot be repaired without modifying diagnostics;
- server config is inaccessible;
- public DNS/TLS is outside current permissions;
- repair requires touching live trading or unrelated systems;
- public URL still fails after local server route is confirmed.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: verify public factor page deployment
```

Final response should include:

- commit hash
- summary verdict
- root cause of page not opening
- local file / QA result
- public URL status before and after
- server config / permission finding
- repair applied
- files changed
- confirmation no factor/signal/diagnostic changes
- remaining limitations
- recommended next PM
