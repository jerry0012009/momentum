# ops mobile ui deployment notes

## Live shape
- `/ops/` → Apache-served mobile control panel (`index.php` + `api.php`)
- `/ops/term/` → proxied ttyd terminal
- ttyd session → `tmux new-session -A -s webcli`

## Apache include applied live
File: `/etc/apache2/conf-available/jp-jerrypsy-top-ops-terminal.conf`

```apache
# Protected mobile-friendly tmux console mounted at /ops/.
<LocationMatch "^/ops(?:/.*)?$">
    AuthType Basic
    AuthName "Protected CLI"
    AuthUserFile /etc/apache2/.htpasswd-ops
    Require valid-user
</LocationMatch>

RedirectMatch 302 ^/ops$ /ops/
Alias /ops/ /var/www/html/ops/
<Directory "/var/www/html/ops/">
    AllowOverride None
    Options FollowSymLinks
    DirectoryIndex index.php index.html
    Require all granted
</Directory>

ProxyPass /ops/term/ http://127.0.0.1:7681/ops/term/ retry=0 timeout=86400 upgrade=websocket
ProxyPassReverse /ops/term/ http://127.0.0.1:7681/ops/term/
```

## ttyd override applied live
File: `/etc/systemd/system/ttyd.service.d/override.conf`

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/ttyd -i lo -p 7681 -O -W -w /root -b /ops/term tmux new-session -A -s webcli
```

## Privilege bridge for live Apache
Because `/ops/api.php` runs as `www-data` but the live tmux socket belongs to root, the live host needs:

- wrapper: `/usr/local/bin/ops-tmuxctl`
- sudoers: `/etc/sudoers.d/ops-tmuxctl-www-data`
- socket proxy service: `/etc/systemd/system/ops-tmux-socket-proxy.service`
- proxy script: `/usr/local/bin/tmux_socket_proxy.py`

Why the extra proxy exists:

- the root tmux server uses the default socket under `/tmp/tmux-0/default`
- `apache2.service` has `PrivateTmp=yes`
- so HTTPS requests handled by Apache cannot see the real root `/tmp`

Fix:

- keep the real tmux server where it is
- proxy that Unix socket to a shared path: `/run/ops-tmux/default`
- point `/usr/local/bin/ops-tmuxctl` at `/run/ops-tmux/default`
- let `api.php` call it via:

```bash
sudo -n /usr/local/bin/ops-tmuxctl ...
```

Encoding note from the live alias debugging round:

- Apache serves `/ops/api.php` under `PHP_SAPI=apache2handler` and this host exposes `LANG=C` there
- tmux treats non-UTF-8 client environments as ASCII-only and replaces non-ASCII window names with `_`
- the symptom was: Chinese window aliases looked correct in CLI tests, but the real HTTPS `/ops/api.php?state=1` response returned `ops____`
- the live fix is to force UTF-8 client mode in the wrapper itself:

```bash
exec /usr/bin/tmux -u -S /run/ops-tmux/default "$@"
```

- keep this in the wrapper, not in `api.php`, so every Apache-triggered tmux command gets the same behavior

## Frontend actions in v1
- pane: left / right / up / down / next / zoom
- window: prev / next / new
- layout: split horizontal / split vertical / tiled / even-horizontal / even-vertical
- keys: copy mode / page up / page down / line scroll up / line scroll down / Enter / Esc / Tab / Ctrl-C
- android-missing keys: arrows / Home / End / Backspace / Delete / Ctrl-A / Ctrl-B / Ctrl-E / Ctrl-L / Ctrl-R / Ctrl-U / Ctrl-K / Ctrl-W / Ctrl-D / Ctrl-Z
- helpers: focus terminal / refresh terminal
- close: close current pane/window safely (`close_current`)
- paste: page-level textarea sends external text into the active pane (`send_text`)
- copy-mode help: page includes instructions + explicit `退出复制模式` button
- terminal-side scroll rail: right side of the tmux iframe includes `上滚 / 下滚` buttons; long-press repeats for phone-friendly history browsing

## Mobile paste behavior
Directly pasting from another app into the embedded ttyd terminal is unreliable on mobile browsers, especially inside an iframe. The intended workflow is:

1. paste text into the page textarea (`外部文本粘贴`)
2. tap `发送到终端`
3. let `api.php?action=send_text` inject it through tmux buffer + bracketed paste

## Suggested usage notes for users
- Need shell cursor movement on Android: use `↑ ↓ ← →`, `Home`, `End`
- Need command-line editing: use `Backspace`, `Del`, `Ctrl-A`, `Ctrl-E`, `Ctrl-U`, `Ctrl-K`, `Ctrl-W`
- Need tmux/readline control: use `Ctrl-B`, `Ctrl-C`, `Ctrl-D`, `Ctrl-Z`, `Ctrl-L`, `Ctrl-R`
- Need history browsing: easiest on phone is the mouse wheel or the terminal-side `上滚 / 下滚` buttons after entering copy mode; `退出复制模式` returns to normal input

## 2026-04 scroll bridge default

- The `/ops/` page now enables a ttyd wheel bridge by default for the right-side `上滚 / 下滚` buttons.
- In the default path, those buttons inject wheel events into the embedded ttyd/xterm iframe so the behavior matches the real mouse wheel more closely.
- This leaves the existing real wheel behavior unchanged.
- Safety fallback: `/ops/?scrollBridge=off` disables the bridge and restores the older API-only button behavior.

## 2026-04 wheel / copy-mode postmortem

Final behavior that tested best in production:

- keep `/ops/` as the outer mobile control page
- let ttyd + xterm + tmux own mouse-wheel behavior inside the terminal
- enable tmux mouse mode with:

```tmux
set -g mouse on
```

- persist that live setting in `/root/.tmux.conf`, then `tmux source-file /root/.tmux.conf`

- keep the page-level copy-mode toggle so users can always exit back to live input
- do **not** auto-enter copy mode from the page-side `上滚 / 下滚` buttons

Important lessons from the debugging round:

- There is no tmux option that makes wheel events scroll the **outer web page**. tmux can only decide what to do **after** the wheel event reaches tmux: forward to the app, enter copy mode, scroll history, or noop.
- The default tmux root-table binding on this host was:

```tmux
bind-key -T root WheelUpPane if-shell -F "#{||:#{pane_in_mode},#{mouse_any_flag}}" { send-keys -M } { copy-mode -e }
```

- That binding explains two user-visible failure modes:
  - wheel can enter tmux copy mode
  - wheel can be forwarded to fullscreen terminal apps that interpret it as app-local navigation
- Frontend wheel interception inside the iframe is fragile and easy to mis-tune. It can fight xterm's own viewport behavior and make the terminal feel worse than the original ttyd page.
- The more stable rollback was to stop translating wheel into synthetic page scrolling and instead restore tmux-native wheel handling.
- Because wheel now intentionally enters tmux history, the UI must keep an explicit enter/exit copy-mode toggle; otherwise users can get "stuck" in history mode and think input is broken.

## Known behavior
- Actions operate on the shared `webcli` tmux session.
- If multiple people are attached to the same tmux session simultaneously, pane/window focus changes are shared.
- This is optimized for phone ergonomics, not multi-user isolation.
