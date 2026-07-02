<?php
$clipboardBridgeMode = !isset($_GET['clipboardBridge']) || $_GET['clipboardBridge'] !== 'off';
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');
?>
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>OPS Mobile Panel</title>
  <style>
    :root {
      --bg: #0b1020;
      --bg-soft: #141b34;
      --card: rgba(20, 27, 52, 0.92);
      --line: rgba(255,255,255,0.08);
      --text: #edf2ff;
      --muted: #9fb0d9;
      --accent: #5ea1ff;
      --ok: #2bd576;
      --danger: #ff6b6b;
      --shadow: 0 10px 30px rgba(0,0,0,0.28);
      --radius: 16px;
      --btn-radius: 12px;
      --terminal-height: clamp(520px, 76vh, 960px);
      --font-sans: "Inter", "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "Droid Sans Fallback", "WenQuanYi Micro Hei", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; height: 100%; background: radial-gradient(circle at top, #152246 0%, var(--bg) 45%, #060912 100%); color: var(--text); font-family: var(--font-sans); text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
    body { min-height: 100%; }

    .page {
      max-width: 1180px;
      margin: 0 auto;
      padding: max(10px, env(safe-area-inset-top)) 10px max(10px, env(safe-area-inset-bottom)) 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-height: 100vh;
    }

    .hero, .group, .terminal-shell {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }

    .hero {
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    h1 {
      margin: 0;
      font-size: 18px;
      line-height: 1.2;
    }

    .subtitle {
      color: var(--muted);
      font-size: 12.5px;
      line-height: 1.45;
    }

    .badge {
      padding: 5px 9px;
      border-radius: 999px;
      font-size: 11px;
      background: rgba(94, 161, 255, 0.12);
      color: #cfe0ff;
      white-space: nowrap;
    }

    .status-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
      font-size: 12px;
      color: var(--muted);
    }

    .window-alias-panel {
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(240px, 0.9fr);
      gap: 10px;
      align-items: stretch;
    }

    .window-alias-main,
    .window-alias-editor {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(8, 13, 27, 0.42);
      padding: 10px 12px;
    }

    .window-alias-label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .window-alias-display {
      margin-top: 4px;
      font-size: clamp(18px, 3.4vw, 28px);
      line-height: 1.22;
      font-weight: 600;
      color: #ffffff;
      word-break: break-word;
      overflow-wrap: anywhere;
      font-family: inherit;
      letter-spacing: 0;
    }

    .window-alias-meta {
      margin-top: 4px;
      font-size: 12px;
      color: var(--muted);
      line-height: 1.5;
      font-family: inherit;
    }

    .window-alias-editor {
      display: flex;
      flex-direction: column;
      gap: 8px;
      justify-content: center;
    }

    .input-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
    }

    input[type="text"] {
      width: 100%;
      min-height: 40px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(7, 11, 22, 0.78);
      color: var(--text);
      padding: 8px 12px;
      font: inherit;
      font-family: inherit;
    }

    .window-list {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 2px 0 4px;
      scrollbar-width: thin;
    }

    .window-chip {
      min-height: 42px;
      padding: 7px 10px;
      border-radius: 10px;
      font-size: 12px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      width: auto;
      min-width: 150px;
      flex: 0 0 auto;
      text-align: left;
    }

    .window-chip.is-active {
      background: linear-gradient(180deg, rgba(94,161,255,0.26), rgba(94,161,255,0.12));
      border-color: rgba(94,161,255,0.42);
    }

    .window-status-icon {
      width: 22px;
      height: 22px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex: 0 0 22px;
      font-size: 10px;
      font-weight: 800;
      color: #06111f;
      background: var(--muted);
    }

    .window-chip.status-running .window-status-icon {
      background: var(--ok);
    }

    .window-chip.status-needs-approval .window-status-icon {
      background: #ffd166;
    }

    .window-chip.status-paused .window-status-icon {
      background: #b58cff;
    }

    .window-chip.status-idle .window-status-icon {
      background: #9fb0d9;
    }

    .window-chip-main {
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .window-chip-top {
      display: flex;
      align-items: center;
      gap: 6px;
      min-width: 0;
    }

    .window-chip-index,
    .window-chip-status {
      color: #cfe0ff;
      opacity: 0.78;
      font-size: 11px;
      white-space: nowrap;
    }

    .window-chip-name {
      max-width: clamp(120px, 38vw, 260px);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-family: inherit;
      letter-spacing: 0;
    }

    .window-chip-sub {
      max-width: clamp(120px, 38vw, 260px);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: var(--muted);
      font-size: 11px;
      font-weight: 500;
    }

    .terminal-actions {
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 6px;
    }

    .toolbar-note {
      font-size: 11px;
      color: var(--muted);
      line-height: 1.4;
    }

    .controls {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 10px;
    }

    .group {
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .group h2 {
      margin: 0;
      font-size: 13px;
      color: #dbe6ff;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
    }

    .grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .grid.four { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .grid.six { grid-template-columns: repeat(6, minmax(0, 1fr)); }

    textarea {
      width: 100%;
      min-height: 92px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(7, 11, 22, 0.78);
      color: var(--text);
      padding: 10px 12px;
      font: inherit;
      resize: vertical;
    }

    .quick-input {
      min-height: 60px;
      resize: none;
    }

    code {
      word-break: break-word;
    }

    button {
      appearance: none;
      border: 1px solid rgba(255,255,255,0.08);
      background: linear-gradient(180deg, rgba(94,161,255,0.18), rgba(94,161,255,0.08));
      color: var(--text);
      min-height: 40px;
      border-radius: var(--btn-radius);
      padding: 8px 10px;
      font-size: 13px;
      font-weight: 650;
      line-height: 1.15;
      letter-spacing: 0.005em;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
      transition: transform .08s ease, background .12s ease, border-color .12s ease, opacity .12s ease;
      touch-action: manipulation;
      word-break: break-word;
    }

    button:active,
    button.is-holding {
      transform: scale(0.98);
      background: linear-gradient(180deg, rgba(94,161,255,0.28), rgba(94,161,255,0.16));
      border-color: rgba(255,255,255,0.18);
    }

    button.secondary { background: rgba(255,255,255,0.04); }
    button.danger { background: linear-gradient(180deg, rgba(255,107,107,0.22), rgba(255,107,107,0.12)); }
    button.wide { grid-column: span 2; }
    button.full { grid-column: 1 / -1; }
    button:disabled { opacity: 1; cursor: default; }

    .terminal-stage {
      display: flex;
      align-items: stretch;
      gap: 8px;
      min-height: 520px;
      flex: 1;
    }

    .scroll-rail {
      width: 62px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 0 0 62px;
    }

    .scroll-button {
      flex: 1;
      min-height: 0;
      padding: 8px 6px;
      line-height: 1.15;
      font-size: 12px;
      user-select: none;
      -webkit-user-select: none;
      touch-action: none;
    }

    .repeat-button {
      user-select: none;
      -webkit-user-select: none;
      touch-action: none;
    }

    .scroll-button strong {
      display: block;
      font-size: 16px;
      margin-bottom: 2px;
    }

    .scroll-tip {
      font-size: 10px;
      color: var(--muted);
      line-height: 1.35;
      text-align: center;
      padding: 0 2px;
    }

    .terminal-wrap {
      flex: 1;
      min-width: 0;
      display: flex;
    }

    .hint {
      font-size: 11px;
      color: var(--muted);
      line-height: 1.4;
    }

    .terminal-shell {
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;
      min-height: 520px;
    }

    .terminal-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 11px;
    }

    .terminal-toolbar strong {
      color: var(--text);
      font-weight: 650;
    }

    .terminal-toolbar code {
      font-size: 11px;
    }

    iframe {
      width: 100%;
      min-height: 520px;
      height: var(--terminal-height);
      border: 0;
      border-radius: 12px;
      background: #000;
    }

    details.group summary {
      cursor: pointer;
      list-style: none;
      font-size: 13px;
      font-weight: 650;
      color: #dbe6ff;
    }

    details.group summary::-webkit-details-marker {
      display: none;
    }

    details.group[open] summary {
      margin-bottom: 6px;
    }

    .toast {
      position: fixed;
      left: 50%;
      bottom: calc(16px + env(safe-area-inset-bottom));
      transform: translateX(-50%) translateY(10px);
      background: rgba(7, 11, 22, 0.94);
      border: 1px solid rgba(255,255,255,0.1);
      color: var(--text);
      padding: 10px 14px;
      border-radius: 999px;
      font-size: 13px;
      opacity: 0;
      pointer-events: none;
      transition: opacity .18s ease, transform .18s ease;
      box-shadow: var(--shadow);
      z-index: 10;
    }

    .toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }

    @media (max-width: 900px) {
      .controls { grid-template-columns: 1fr; }
      .terminal-actions { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .grid.six { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .window-alias-panel { grid-template-columns: 1fr; }
    }

    @media (max-width: 760px) {
      .page {
        gap: 8px;
        padding-left: 8px;
        padding-right: 8px;
      }
      .title-row {
        align-items: flex-start;
      }
      .title-row,
      .status-row,
      .terminal-toolbar {
        flex-direction: column;
        align-items: flex-start;
      }
      .grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      .grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid.four { grid-template-columns: repeat(4, minmax(0, 1fr)); }
      .scroll-rail {
        width: 56px;
        flex-basis: 56px;
      }
      .scroll-button strong { font-size: 15px; }
      button {
        min-height: 38px;
        padding: 7px 8px;
        font-size: 12px;
      }
      textarea {
        min-height: 84px;
      }
      .quick-input {
        min-height: 56px;
      }
      .subtitle {
        max-height: 2.9em;
        overflow: hidden;
      }
      .input-row {
        grid-template-columns: 1fr;
      }
      :root { --terminal-height: clamp(460px, 72vh, 760px); }
      .terminal-stage,
      .terminal-shell,
      iframe {
        min-height: 460px;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="title-row">
        <h1>OPS 手机控制面板</h1>
        <div class="badge" id="session-badge">tmux: 读取中…</div>
      </div>
      <div class="window-alias-panel">
        <div class="window-alias-main">
          <div class="window-alias-label">当前窗口备注</div>
          <div class="window-alias-display" id="window-alias-display">读取中…</div>
          <div class="window-alias-meta" id="window-alias-meta">窗口信息读取中…</div>
        </div>
        <div class="window-alias-editor">
          <div class="window-alias-label">修改当前窗口备注</div>
          <div class="input-row">
            <input id="window-alias-input" type="text" maxlength="64" placeholder="例如：rank213实盘维护">
            <button id="window-alias-save">保存备注</button>
          </div>
          <div class="hint">直接写入 tmux 当前 window name。保存时会对当前窗口关闭 automatic-rename，避免备注被命令名自动覆盖。</div>
        </div>
      </div>
      <div class="subtitle">
        这个页现在优先把高度留给终端，按钮层只负责补手机端缺失的 tmux / CLI 操作。外部复制内容时，优先用下面的“手机输入 / 粘贴发送”，不要指望 iframe 里的 ttyd 稳定吃到系统剪贴板。
      </div>
      <div class="window-list" id="window-list"></div>
      <div class="status-row">
        <div id="status-text">状态读取中…</div>
        <div id="last-action">最近操作：无</div>
      </div>
      <?php if (!$clipboardBridgeMode): ?>
      <div class="toolbar-note">剪贴板桥接已关闭：当前不会自动把复制模式选区写入浏览器剪贴板。</div>
      <?php endif; ?>
    </section>

    <section class="terminal-shell">
      <div class="terminal-toolbar">
        <div><strong>终端还是原来的 ttyd + tmux</strong>，这里只是把手机端缺的键补在外围。</div>
        <div>直连路径：<code>/ops/term/</code></div>
      </div>
      <div class="terminal-stage">
        <div class="terminal-wrap">
          <iframe id="terminal-frame" src="term/" title="OPS terminal" tabindex="0"></iframe>
        </div>
        <div class="scroll-rail">
          <button class="scroll-button" data-repeat-action="scroll_up"><strong>▲</strong>上滚</button>
          <button class="scroll-button" data-repeat-action="scroll_down"><strong>▼</strong>下滚</button>
          <div class="scroll-tip">长按连滚<br>模拟真实滚轮</div>
        </div>
      </div>
      <div class="terminal-actions">
        <button id="open-term-direct">直开终端</button>
        <button class="secondary" id="open-term-new-tab">新标签页</button>
        <button class="secondary" data-action="focus_terminal">聚焦终端</button>
        <button class="secondary" data-action="refresh_terminal">刷新</button>
        <button data-action="copy_mode_toggle" data-copy-toggle>进入复制模式</button>
        <button class="danger" data-action="ctrl_c">Ctrl-C</button>
      </div>
      <div class="toolbar-note">
        现在滚轮优先走 tmux 历史；看完后点 <code>退出复制模式</code> 回到底部继续输入。只想回到纯终端手感就点 <code>直开终端</code>。
      </div>
    </section>

    <section class="controls">
      <div class="group">
        <h2>Tmux 视图</h2>
        <div class="grid four">
          <button data-action="pane_up">Pane ↑</button>
          <button data-action="pane_next">下个 Pane</button>
          <button data-action="pane_down">Pane ↓</button>
          <button data-action="pane_zoom">放大</button>
          <button data-action="pane_left">Pane ←</button>
          <button data-action="window_prev">窗 ←</button>
          <button data-action="window_next">窗 →</button>
          <button data-action="pane_right">Pane →</button>
          <button data-action="split_h">左右分</button>
          <button data-action="split_v">上下分</button>
          <button data-action="layout_tiled">平铺</button>
          <button data-action="window_new">新窗</button>
          <button data-action="layout_even_h">横均分</button>
          <button data-action="layout_even_v">纵均分</button>
          <button class="secondary wide" data-action="focus_terminal">聚焦终端</button>
        </div>
        <div class="hint">把 pane、window、分屏相关的低级 tmux 操作收在一块，少来回找按钮。</div>
      </div>

      <div class="group">
        <h2>常用按键 / 浏览</h2>
        <div class="grid four">
          <button data-action="copy_mode_toggle" data-copy-toggle>进入复制模式</button>
          <button data-action="copy_mode_exit">强制退出复制模式</button>
          <button data-action="page_up">PgUp</button>
          <button data-action="page_down">PgDn</button>
          <button data-action="enter">Enter</button>
          <button data-action="escape">Esc</button>
          <button data-action="tab">Tab</button>
          <button class="danger" data-action="ctrl_c">Ctrl-C</button>
          <button class="danger wide" data-action="close_current">关当前 pane / 窗</button>
          <button class="secondary full" data-action="refresh_terminal">刷新终端</button>
        </div>
        <div class="hint">适合 less / tail / 命令中断 / copy mode。右侧上下滚现在直接桥接到 ttyd 终端滚轮；PgUp / PgDn 仍只在复制模式里工作。</div>
      </div>

      <div class="group">
        <h2>方向 / 编辑键</h2>
        <div class="grid four">
          <button class="repeat-button" data-repeat-action="home">Home</button>
          <button class="repeat-button" data-repeat-action="arrow_up">↑</button>
          <button class="repeat-button" data-repeat-action="end">End</button>
          <button class="repeat-button" data-repeat-action="backspace">⌫</button>
          <button class="repeat-button" data-repeat-action="arrow_left">←</button>
          <button class="repeat-button" data-repeat-action="arrow_down">↓</button>
          <button class="repeat-button" data-repeat-action="arrow_right">→</button>
          <button class="repeat-button" data-repeat-action="delete">Del</button>
        </div>
        <div class="hint">适合 shell 光标移动、命令行编辑、less/vim/top；这组键支持长按连发。</div>
      </div>

      <div class="group">
        <h2>Ctrl 快捷键</h2>
        <div class="grid four">
          <button data-action="ctrl_a">Ctrl-A</button>
          <button data-action="ctrl_e">Ctrl-E</button>
          <button data-action="ctrl_u">Ctrl-U</button>
          <button data-action="ctrl_k">Ctrl-K</button>
          <button data-action="ctrl_w">Ctrl-W</button>
          <button data-action="ctrl_d">Ctrl-D</button>
          <button data-action="ctrl_z">Ctrl-Z</button>
          <button data-action="ctrl_l">Ctrl-L</button>
          <button data-action="ctrl_r">Ctrl-R</button>
          <button data-action="ctrl_b">Ctrl-B</button>
          <button class="danger" data-action="ctrl_c">Ctrl-C</button>
          <button data-action="tab">Tab</button>
        </div>
        <div class="hint">覆盖 bash / zsh / readline 里最常用的一批：行首行尾、删词、搜索、tmux 前缀、中断等。</div>
      </div>

      <div class="group">
        <h2>手机直接输入（更稳）</h2>
        <textarea id="mobile-input" class="quick-input" autocapitalize="off" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="send" placeholder="点这里直接唤起手机键盘；输入后可发送到当前 tmux pane。适合命令、短句、补字。"></textarea>
        <div class="grid two">
          <button id="mobile-send">发送</button>
          <button id="mobile-send-enter">发送 + 回车</button>
          <button class="secondary" data-action="focus_terminal">聚焦终端</button>
          <button class="secondary" id="mobile-clear">清空</button>
        </div>
        <div class="hint">这组输入框不依赖 iframe 焦点，直接用网页原生输入法/软键盘录入，再转发到当前 tmux pane。对手机端比直接点 ttyd 更稳。</div>
      </div>

      <div class="group">
        <h2>外部文本粘贴</h2>
        <textarea id="paste-box" placeholder="先把外部复制的文本粘到这里，再点下方按钮发送到当前 tmux pane。支持多行。"></textarea>
        <div class="grid two">
          <button data-action="send_paste">发送粘贴</button>
          <button class="secondary" data-action="clear_paste">清空</button>
        </div>
        <div class="hint">原因：手机浏览器里的 iframe + ttyd 对系统剪贴板支持不稳定，所以这里提供一个更稳的粘贴入口。</div>
      </div>

      <details class="group">
        <summary>复制模式说明</summary>
        <div class="hint">
          1. 点 <strong>复制模式</strong> 进入 tmux history 浏览。<br>
          2. <strong>右侧上滚 / 下滚</strong> 现在会模拟终端里的真实鼠标滚轮，所以行为尽量和你直接滚屏一致；<strong>PgUp / PgDn</strong> 仍只在复制模式里工作。<br>
          3. 现在鼠标滚轮也会走 tmux history；看完后点 <strong>退复制</strong>，回到正常输入。<br>
          4. 在复制模式里拖拽选中一段终端文字后，网页会尝试把 tmux 复制缓冲区同步到浏览器剪贴板；如果浏览器拒绝剪贴板权限，可以用 <code>?clipboardBridge=off</code> 临时关闭。
        </div>
      </details>
    </section>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    const statusText = document.getElementById('status-text');
    const lastAction = document.getElementById('last-action');
    const sessionBadge = document.getElementById('session-badge');
    const windowAliasDisplay = document.getElementById('window-alias-display');
    const windowAliasMeta = document.getElementById('window-alias-meta');
    const windowAliasInput = document.getElementById('window-alias-input');
    const windowAliasSave = document.getElementById('window-alias-save');
    const windowList = document.getElementById('window-list');
    const toast = document.getElementById('toast');
    const frame = document.getElementById('terminal-frame');
    const pasteBox = document.getElementById('paste-box');
    const mobileInput = document.getElementById('mobile-input');
    const mobileSend = document.getElementById('mobile-send');
    const mobileSendEnter = document.getElementById('mobile-send-enter');
    const mobileClear = document.getElementById('mobile-clear');
    const openTermDirect = document.getElementById('open-term-direct');
    const openTermNewTab = document.getElementById('open-term-new-tab');
    const copyToggleButtons = Array.from(document.querySelectorAll('[data-copy-toggle]'));
    const params = new URLSearchParams(window.location.search);
    const session = params.get('session') || 'webcli';
    const scrollBridgeMode = params.get('scrollBridge') !== 'off';
    const clipboardBridgeMode = params.get('clipboardBridge') !== 'off';
    const apiBase = `api.php${params.toString() ? `?${params.toString()}` : ''}`;

    let toastTimer = null;
    const pendingActions = new Set();
    const repeatStops = new Set();
    let isCopyMode = false;
    let currentWindowId = null;
    let aliasDraftDirty = false;
    let clipboardSelectionText = '';
    let clipboardBridgeTargetWindow = null;
    let clipboardBridgeSelectionDispose = null;
    let clipboardBridgePointerCleanup = null;
    let clipboardBridgeBindTimer = null;
    let clipboardBridgeFailureNotified = false;
    let clipboardPointerStart = null;
    let clipboardPointerDragged = false;

    function resolveTerminalSrc() {
      const path = window.location.pathname || '/';
      if (path.includes('/ops/')) {
        return directTermUrl();
      }
      return `http://127.0.0.1:7681/ops/term/${window.location.search || ''}`;
    }

    function showToast(text) {
      toast.textContent = text;
      toast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('show'), 1800);
    }

    function clearClipboardBridge() {
      clearTimeout(clipboardBridgeBindTimer);
      clipboardBridgeBindTimer = null;
      clipboardBridgeSelectionDispose?.dispose?.();
      clipboardBridgeSelectionDispose = null;
      clipboardBridgePointerCleanup?.();
      clipboardBridgePointerCleanup = null;
      clipboardBridgeTargetWindow = null;
      clipboardSelectionText = '';
      clipboardBridgeFailureNotified = false;
      clipboardPointerStart = null;
      clipboardPointerDragged = false;
    }

    function copyTextLegacy(text) {
      const helper = document.createElement('textarea');
      helper.value = text;
      helper.setAttribute('readonly', 'readonly');
      helper.setAttribute('aria-hidden', 'true');
      helper.style.position = 'fixed';
      helper.style.top = '-9999px';
      helper.style.left = '-9999px';
      helper.style.opacity = '0';
      document.body.appendChild(helper);
      helper.focus({ preventScroll: true });
      helper.select();
      helper.setSelectionRange(0, helper.value.length);
      let ok = false;
      try {
        ok = document.execCommand('copy');
      } catch (_) {}
      helper.remove();
      return ok;
    }

    async function writeSelectionToClipboard(text, sourceWindow) {
      if (!text) {
        return false;
      }

      const candidates = [
        () => navigator.clipboard?.writeText?.(text),
        () => sourceWindow?.navigator?.clipboard?.writeText?.(text)
      ];

      for (const attempt of candidates) {
        try {
          const result = attempt?.();
          if (result && typeof result.then === 'function') {
            await result;
            return true;
          }
        } catch (_) {}
      }

      return copyTextLegacy(text);
    }

    async function fetchLatestTmuxBuffer() {
      const res = await fetch(apiBase, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'clipboard_buffer_latest', session })
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || '读取 tmux 缓冲区失败');
      }
      return {
        bufferName: data.bufferName || '',
        bufferSize: Number(data.bufferSize || 0),
        bufferText: data.bufferText || ''
      };
    }

    function scheduleClipboardBridgeBind(retryCount = 0) {
      if (!clipboardBridgeMode) {
        return;
      }
      clearTimeout(clipboardBridgeBindTimer);
      clipboardBridgeBindTimer = setTimeout(() => bindClipboardBridge(retryCount), retryCount === 0 ? 80 : 220);
    }

    function bindClipboardBridge(retryCount = 0) {
      if (!clipboardBridgeMode) {
        return;
      }

      try {
        const innerWindow = frame.contentWindow;
        const innerDoc = innerWindow?.document;
        const term = innerWindow?.term;
        if (!innerWindow || !innerDoc || !term || typeof term.getSelection !== 'function' || typeof term.onSelectionChange !== 'function') {
          if (retryCount < 20) {
            scheduleClipboardBridgeBind(retryCount + 1);
          } else if (!clipboardBridgeFailureNotified) {
            clipboardBridgeFailureNotified = true;
            showToast('剪贴板桥接未就绪');
          }
          return;
        }

        if (clipboardBridgeTargetWindow === innerWindow) {
          return;
        }

        clearClipboardBridge();
        clipboardBridgeTargetWindow = innerWindow;
        clipboardBridgeSelectionDispose = term.onSelectionChange(() => {
          try {
            clipboardSelectionText = term.getSelection() || '';
          } catch (_) {
            clipboardSelectionText = '';
          }
        });

        const maybeCopySelection = async () => {
          const text = (() => {
            try {
              return term.getSelection() || clipboardSelectionText || '';
            } catch (_) {
              return clipboardSelectionText || '';
            }
          })();
          if (!text) {
            if (!isCopyMode) {
              return;
            }
            if (!clipboardPointerDragged) {
              return;
            }
            try {
              await new Promise((resolve) => setTimeout(resolve, 60));
              const latestBuffer = await fetchLatestTmuxBuffer();
              if (!latestBuffer.bufferText) {
                return;
              }
              const copied = await writeSelectionToClipboard(latestBuffer.bufferText, innerWindow);
              if (copied) {
                clipboardBridgeFailureNotified = false;
                showToast(`已复制 ${latestBuffer.bufferText.length} 字到剪贴板`);
              } else if (!clipboardBridgeFailureNotified) {
                clipboardBridgeFailureNotified = true;
                showToast('浏览器拒绝写入剪贴板');
              }
            } catch (_) {}
            return;
          }

          const ok = await writeSelectionToClipboard(text, innerWindow);
          if (ok) {
            clipboardBridgeFailureNotified = false;
            showToast(`已复制 ${text.length} 字到剪贴板`);
          } else if (!clipboardBridgeFailureNotified) {
            clipboardBridgeFailureNotified = true;
            showToast('浏览器拒绝写入剪贴板');
          }
        };

        const pointerUpHandler = () => {
          maybeCopySelection();
          clipboardPointerStart = null;
          clipboardPointerDragged = false;
          setTimeout(refreshState, 180);
        };
        const pointerDownHandler = (event) => {
          if (!isCopyMode) {
            return;
          }
          clipboardPointerStart = {
            x: Number(event.clientX || 0),
            y: Number(event.clientY || 0)
          };
          clipboardPointerDragged = false;
        };
        const pointerMoveHandler = (event) => {
          if (!clipboardPointerStart) {
            return;
          }
          const dx = Math.abs(Number(event.clientX || 0) - clipboardPointerStart.x);
          const dy = Math.abs(Number(event.clientY || 0) - clipboardPointerStart.y);
          if (dx >= 4 || dy >= 4) {
            clipboardPointerDragged = true;
          }
        };
        const keyUpHandler = (event) => {
          if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'c') {
            maybeCopySelection();
          }
        };

        innerDoc.addEventListener('pointerdown', pointerDownHandler, true);
        innerDoc.addEventListener('pointermove', pointerMoveHandler, true);
        innerDoc.addEventListener('pointerup', pointerUpHandler, true);
        innerDoc.addEventListener('mouseup', pointerUpHandler, true);
        innerDoc.addEventListener('touchend', pointerUpHandler, true);
        innerDoc.addEventListener('keyup', keyUpHandler, true);
        clipboardBridgePointerCleanup = () => {
          innerDoc.removeEventListener('pointerdown', pointerDownHandler, true);
          innerDoc.removeEventListener('pointermove', pointerMoveHandler, true);
          innerDoc.removeEventListener('pointerup', pointerUpHandler, true);
          innerDoc.removeEventListener('mouseup', pointerUpHandler, true);
          innerDoc.removeEventListener('touchend', pointerUpHandler, true);
          innerDoc.removeEventListener('keyup', keyUpHandler, true);
        };
      } catch (_) {
        if (retryCount < 20) {
          scheduleClipboardBridgeBind(retryCount + 1);
        }
      }
    }

    function directTermUrl() {
      return `term/${window.location.search || ''}`;
    }

    function updateCopyModeUi(nextCopyMode) {
      isCopyMode = Boolean(nextCopyMode);
      copyToggleButtons.forEach((button) => {
        button.textContent = isCopyMode ? '退出复制模式' : '进入复制模式';
        button.classList.toggle('danger', isCopyMode);
      });
      if (!isCopyMode) {
        clipboardSelectionText = '';
      }
    }

    function syncDocumentTitle(alias) {
      const cleanAlias = (alias || '').trim();
      document.title = cleanAlias ? `OPS / ${cleanAlias}` : 'OPS 手机控制面板';
    }

    function parseWindowFromState(state) {
      const text = typeof state === 'string' ? state : '';
      const match = text.match(/window\s+(\d+):(.+?)\s+\|\s+pane\b/);
      if (!match) {
        return null;
      }
      return {
        index: Number(match[1]),
        name: (match[2] || '').trim()
      };
    }

    function renderWindowList(windows, activeWindowId) {
      windowList.textContent = '';
      if (!Array.isArray(windows) || !windows.length) {
        return;
      }
      windows.forEach((windowMeta) => {
        const statusClass = windowMeta.statusClass || windowMeta.status || 'idle';
        const statusLabel = windowMeta.statusLabel || '未知';
        const command = windowMeta.currentCommand || '';
        const panes = Number(windowMeta.panes || 0);
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `window-chip status-${statusClass}${windowMeta.active ? ' is-active' : ' secondary'}`;
        button.title = `窗口 #${windowMeta.index} · ${statusLabel}${command ? ` · ${command}` : ''}`;

        const icon = document.createElement('span');
        icon.className = 'window-status-icon';
        icon.textContent = windowMeta.statusIcon || '-';

        const main = document.createElement('span');
        main.className = 'window-chip-main';

        const top = document.createElement('span');
        top.className = 'window-chip-top';

        const index = document.createElement('span');
        index.className = 'window-chip-index';
        index.textContent = `#${windowMeta.index}`;

        const name = document.createElement('span');
        name.className = 'window-chip-name';
        name.textContent = windowMeta.name || `window-${windowMeta.index}`;

        const status = document.createElement('span');
        status.className = 'window-chip-status';
        status.textContent = statusLabel;

        const sub = document.createElement('span');
        sub.className = 'window-chip-sub';
        sub.textContent = `${command || 'shell'}${panes > 1 ? ` · ${panes} panes` : ''}`;

        top.append(index, name, status);
        main.append(top, sub);
        button.append(icon, main);
        if (windowMeta.id === activeWindowId) {
          button.disabled = true;
        } else {
          button.addEventListener('click', () => sendAction('window_focus', { window: String(windowMeta.index) }));
        }
        windowList.appendChild(button);
      });
    }

    function applySnapshot(data, keepLastAction = false) {
      statusText.textContent = `当前：${data.state || '未知'}`;
      sessionBadge.textContent = `tmux: ${data.session || session}`;
      updateCopyModeUi(data.copyMode);

      const parsedWindow = parseWindowFromState(data.state);
      const currentWindow = data.currentWindow || (parsedWindow ? {
        index: parsedWindow.index,
        name: parsedWindow.name,
        id: null,
        active: true,
        automaticRename: null
      } : null);
      const alias = currentWindow?.name || data.windowLabel || data.currentAlias || parsedWindow?.name || '未命名窗口';
      const currentStatus = currentWindow?.statusLabel ? ` · ${currentWindow.statusLabel}` : '';
      const currentCommand = currentWindow?.currentCommand ? ` · ${currentWindow.currentCommand}` : '';
      const aliasMeta = currentWindow
        ? `窗口 #${currentWindow.index}${currentStatus}${currentCommand}${typeof currentWindow.automaticRename === 'boolean' ? ` · ${currentWindow.automaticRename ? '自动改名开启' : '自动改名关闭'}` : ''}`
        : '当前窗口信息不可用';

      windowAliasDisplay.textContent = alias;
      windowAliasMeta.textContent = aliasMeta;
      syncDocumentTitle(alias);
      renderWindowList(data.windows || [], currentWindow?.id || null);

      const nextWindowId = currentWindow?.id || null;
      const preserveDraft = aliasDraftDirty && document.activeElement === windowAliasInput && currentWindowId === nextWindowId;
      if (!preserveDraft) {
        windowAliasInput.value = currentWindow?.name || '';
        aliasDraftDirty = false;
      }
      currentWindowId = nextWindowId;

      if (!keepLastAction && data.label) {
        lastAction.textContent = `最近操作：${data.label}${data.noop ? '（保持原状）' : ''}`;
      }
    }

    function focusTerminalInput() {
      try {
        frame.focus({ preventScroll: true });
      } catch (_) {
        try { frame.focus(); } catch (_) {}
      }

      try {
        const innerWindow = frame.contentWindow;
        innerWindow?.focus?.();
        const doc = innerWindow?.document;
        const helper = doc?.querySelector?.('.xterm-helper-textarea, textarea.xterm-helper-textarea, textarea');
        if (helper) {
          helper.focus({ preventScroll: true });
          return true;
        }
        doc?.body?.focus?.();
        return true;
      } catch (_) {
        return false;
      }
    }

    function stopAllRepeats() {
      repeatStops.forEach((stop) => stop());
    }

    function dismissSoftInput() {
      try { mobileInput?.blur?.(); } catch (_) {}
      try { pasteBox?.blur?.(); } catch (_) {}
      try { document.activeElement?.blur?.(); } catch (_) {}

      try {
        const innerDoc = frame.contentWindow?.document;
        innerDoc?.activeElement?.blur?.();
        const helper = innerDoc?.querySelector?.('.xterm-helper-textarea, textarea.xterm-helper-textarea, textarea');
        helper?.blur?.();
      } catch (_) {}
    }

    function dispatchTerminalWheel(action) {
      try {
        const innerWindow = frame.contentWindow;
        const doc = innerWindow?.document;
        const target = doc?.querySelector?.('.xterm-screen') || doc?.querySelector?.('.xterm') || doc?.querySelector?.('.xterm-viewport');
        if (!innerWindow || !doc || !target || typeof innerWindow.WheelEvent !== 'function') {
          return false;
        }

        const rect = target.getBoundingClientRect();
        const wheelEvent = new innerWindow.WheelEvent('wheel', {
          bubbles: true,
          cancelable: true,
          deltaY: action === 'scroll_up' ? -240 : 240,
          deltaMode: 0,
          clientX: rect.left + Math.max(10, Math.min(rect.width / 2, 80)),
          clientY: rect.top + Math.max(10, Math.min(rect.height / 2, 80))
        });
        target.dispatchEvent(wheelEvent);
        setTimeout(refreshState, 350);
        return true;
      } catch (_) {
        return false;
      }
    }

    function runRepeatAction(action) {
      if (scrollBridgeMode && (action === 'scroll_up' || action === 'scroll_down')) {
        const ok = dispatchTerminalWheel(action);
        if (!ok) {
          showToast('滚轮桥接未就绪');
        }
        return;
      }
      sendAction(action);
    }

    async function sendAction(action, extra = {}) {
      if (action === 'focus_terminal') {
        stopAllRepeats();
        focusTerminalInput();
        showToast('已尝试聚焦终端');
        return;
      }

      if (action === 'refresh_terminal') {
        frame.src = frame.dataset.termSrc;
        showToast('终端已刷新');
        return;
      }

      if (action === 'clear_paste') {
        pasteBox.value = '';
        pasteBox.focus();
        showToast('已清空粘贴框');
        return false;
      }

      if (action === 'send_paste') {
        const text = pasteBox.value;
        if (!text) {
          showToast('先粘点文本进去');
          pasteBox.focus();
          return false;
        }
        action = 'send_text';
        extra = { ...extra, text, clientSource: 'paste-box' };
      }

      const pendingKey = `${action}::${extra.text ? 'text' : ''}`;
      if (pendingActions.has(pendingKey)) {
        return false;
      }
      pendingActions.add(pendingKey);

      try {
        const res = await fetch(apiBase, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action, session, ...extra })
        });
        const data = await res.json();
        if (!res.ok || !data.ok) {
          throw new Error(data.error || '请求失败');
        }
        applySnapshot(data);
        showToast(data.noop ? (data.note || `已处理：${data.label || action}（保持原状）`) : `已执行：${data.label || action}`);
        if (action === 'send_text') {
          if (extra.clientSource === 'mobile-input') {
            mobileInput.value = '';
            setTimeout(() => mobileInput.focus(), 30);
          } else {
            pasteBox.value = '';
            setTimeout(() => focusTerminalInput(), 30);
          }
        }
        if ((action === 'copy_mode_exit' || action === 'copy_mode_toggle') && !data.copyMode) {
          setTimeout(() => focusTerminalInput(), 30);
        }
        return true;
      } catch (err) {
        showToast(`失败：${err.message}`);
        return false;
      } finally {
        pendingActions.delete(pendingKey);
      }
    }

    async function sendMobileInput(withEnter = false) {
      const text = mobileInput.value;
      if (!text) {
        showToast('先在手机输入框里打字');
        mobileInput.focus();
        return;
      }
      await sendAction('copy_mode_exit');
      const ok = await sendAction('send_text', {
        text,
        clientSource: 'mobile-input'
      });
      if (ok && withEnter) {
        await sendAction('enter');
      }
    }
    function bindRepeatButton(button) {
      const action = button.dataset.repeatAction;
      if (!action) return;

      let repeatTimer = null;
      let repeatInterval = null;
      let activePointerId = null;

      const stop = () => {
        clearTimeout(repeatTimer);
        clearInterval(repeatInterval);
        repeatTimer = null;
        repeatInterval = null;
        activePointerId = null;
        button.classList.remove('is-holding');
      };

      repeatStops.add(stop);

      const start = (event) => {
        event.preventDefault();
        dismissSoftInput();
        stop();
        activePointerId = event.pointerId;
        try { button.setPointerCapture?.(event.pointerId); } catch (_) {}
        button.classList.add('is-holding');
        runRepeatAction(action);
        repeatTimer = setTimeout(() => {
          repeatInterval = setInterval(() => runRepeatAction(action), 140);
        }, 260);
      };

      const stopFromEvent = (event) => {
        if (activePointerId === null || event.pointerId === undefined || event.pointerId === activePointerId) {
          stop();
        }
      };

      button.addEventListener('pointerdown', start);
      button.addEventListener('pointerup', stopFromEvent);
      button.addEventListener('pointercancel', stopFromEvent);
      button.addEventListener('lostpointercapture', stop);
      button.addEventListener('pointerleave', (event) => {
        if (event.buttons === 0) stop();
      });
      button.addEventListener('click', (event) => event.preventDefault());
    }

    async function refreshState() {
      try {
        const stateUrl = `${apiBase}${apiBase.includes('?') ? '&' : '?'}state=1`;
        const res = await fetch(stateUrl, { cache: 'no-store' });
        const data = await res.json();
        if (data.ok) {
          applySnapshot(data, true);
        }
      } catch (_) {}
    }

    frame.dataset.termSrc = resolveTerminalSrc();
    frame.src = frame.dataset.termSrc;
    sessionBadge.textContent = `tmux: ${session}`;
    updateCopyModeUi(false);
    syncDocumentTitle('');
    if (!scrollBridgeMode) {
      lastAction.textContent = '最近操作：滚轮桥接已关闭';
    }

    document.querySelectorAll('button[data-action]').forEach((button) => {
      button.addEventListener('pointerdown', (event) => {
        const action = button.dataset.action;
        if (action && action !== 'focus_terminal' && action !== 'clear_paste') {
          event.preventDefault();
          dismissSoftInput();
        }
      });
      button.addEventListener('click', (event) => {
        event.preventDefault();
        const action = button.dataset.action;
        if (action && action !== 'focus_terminal' && action !== 'clear_paste') {
          dismissSoftInput();
        }
        sendAction(action);
      });
    });

    document.querySelectorAll('button[data-repeat-action]').forEach(bindRepeatButton);

    mobileSend?.addEventListener('click', () => sendMobileInput(false));
    mobileSendEnter?.addEventListener('click', () => sendMobileInput(true));
    mobileClear?.addEventListener('click', () => {
      mobileInput.value = '';
      mobileInput.focus();
      showToast('已清空手机输入框');
    });
    mobileInput?.addEventListener('keydown', (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        sendMobileInput(true);
      }
    });
    windowAliasInput?.addEventListener('input', () => {
      aliasDraftDirty = true;
    });
    windowAliasInput?.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        windowAliasSave?.click();
      }
    });
    windowAliasSave?.addEventListener('click', async () => {
      const alias = (windowAliasInput.value || '').trim();
      if (!alias) {
        showToast('先填一个窗口备注');
        windowAliasInput.focus();
        return;
      }
      const ok = await sendAction('window_alias_set', { alias });
      if (ok) {
        aliasDraftDirty = false;
      }
    });
    openTermDirect?.addEventListener('click', () => {
      dismissSoftInput();
      window.location.href = directTermUrl();
    });
    openTermNewTab?.addEventListener('click', () => {
      dismissSoftInput();
      window.open(directTermUrl(), '_blank', 'noopener');
    });

    frame.addEventListener('load', () => {
      showToast('终端已加载');
      clearClipboardBridge();
      scheduleClipboardBridgeBind(0);
      try {
        const innerDoc = frame.contentWindow?.document;
        innerDoc?.addEventListener('pointerdown', () => {
          stopAllRepeats();
          setTimeout(() => focusTerminalInput(), 0);
        }, true);
        innerDoc?.addEventListener('click', () => {
          setTimeout(() => focusTerminalInput(), 0);
        }, true);
      } catch (_) {}
    });

    frame.addEventListener('pointerdown', () => {
      stopAllRepeats();
      setTimeout(() => focusTerminalInput(), 0);
    });
    frame.addEventListener('click', () => {
      setTimeout(() => focusTerminalInput(), 0);
    });
    window.addEventListener('pointerup', stopAllRepeats);
    window.addEventListener('pointercancel', stopAllRepeats);
    window.addEventListener('blur', stopAllRepeats);
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stopAllRepeats();
    });

    refreshState();
    setInterval(refreshState, 4000);
  </script>
</body>
</html>
