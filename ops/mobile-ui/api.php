<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');

function respond(int $status, array $payload): void {
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function tmux_run(array $args, ?string $stdin = null): array {
    $cmd = array_merge(['/usr/bin/sudo', '-n', '/usr/local/bin/ops-tmuxctl'], $args);
    $descriptors = [
        0 => ['pipe', 'r'],
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ];
    $proc = proc_open($cmd, $descriptors, $pipes);
    if (!is_resource($proc)) {
        return ['code' => 127, 'stdout' => '', 'stderr' => 'proc_open failed'];
    }
    if ($stdin !== null && $stdin !== '') {
        fwrite($pipes[0], $stdin);
    }
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    $code = proc_close($proc);
    return ['code' => $code, 'stdout' => trim($stdout), 'stderr' => trim($stderr)];
}

function sanitize_session(?string $raw): string {
    $raw = trim((string) $raw);
    if ($raw === '') {
        return 'webcli';
    }
    if (!preg_match('/^[A-Za-z0-9._:-]{1,64}$/', $raw)) {
        respond(400, ['ok' => false, 'error' => 'Invalid session']);
    }
    return $raw;
}

function sanitize_window_index(?string $raw): string {
    $raw = trim((string) $raw);
    if (!preg_match('/^\d{1,4}$/', $raw)) {
        respond(400, ['ok' => false, 'error' => 'Invalid window index']);
    }
    return $raw;
}

function sanitize_alias(?string $raw): string {
    $alias = preg_replace('/\s+/u', ' ', trim((string) $raw));
    if ($alias === '') {
        respond(400, ['ok' => false, 'error' => '窗口备注不能为空']);
    }
    if (preg_match('/[\x00-\x1F\x7F]/u', $alias)) {
        respond(400, ['ok' => false, 'error' => '窗口备注包含非法控制字符']);
    }
    $length = function_exists('mb_strlen') ? mb_strlen($alias, 'UTF-8') : strlen($alias);
    if ($length > 64) {
        respond(400, ['ok' => false, 'error' => '窗口备注不能超过 64 个字符']);
    }
    return $alias;
}

function current_state(string $session): string {
    $state = tmux_run(['display-message', '-p', '-t', $session . ':.', '#{session_name} | window #{window_index}:#{window_name} | pane #{pane_index} | #{pane_current_command}']);
    if ($state['code'] !== 0 || $state['stdout'] === '') {
        return '无法读取 tmux 状态';
    }
    return $state['stdout'];
}

function parse_window_line(string $line, string $session): ?array {
    $parts = explode("\t", $line);
    if (count($parts) < 5) {
        return null;
    }
    $status = infer_window_status($parts[5] ?? '', (int) ($parts[6] ?? 0), capture_window_text($session, $parts[0] ?? ''));
    return [
        'index' => (int) $parts[0],
        'id' => $parts[1],
        'name' => $parts[2],
        'active' => $parts[3] === '1',
        'automaticRename' => $parts[4] === '1',
        'currentCommand' => $parts[5] ?? '',
        'copyMode' => ($parts[6] ?? '') === '1',
        'panes' => (int) ($parts[7] ?? 0),
        'status' => $status['status'],
        'statusLabel' => $status['label'],
        'statusIcon' => $status['icon'],
        'statusClass' => $status['class'],
    ];
}

function list_windows_meta(string $session): array {
    $result = tmux_run([
        'list-windows',
        '-t',
        $session,
        '-F',
        '#{window_index}' . "\t" . '#{window_id}' . "\t" . '#{window_name}' . "\t" . '#{?window_active,1,0}' . "\t" . '#{?automatic-rename,1,0}' . "\t" . '#{pane_current_command}' . "\t" . '#{pane_in_mode}' . "\t" . '#{window_panes}',
    ]);
    if ($result['code'] !== 0) {
        return [];
    }
    $windows = [];
    foreach (preg_split('/\r?\n/', trim($result['stdout'])) as $line) {
        $line = trim($line);
        if ($line === '') {
            continue;
        }
        $parsed = parse_window_line($line, $session);
        if ($parsed !== null) {
            $windows[] = $parsed;
        }
    }
    return $windows;
}

function capture_window_text(string $session, string $windowIndex): string {
    if ($session === '' || !preg_match('/^\d{1,4}$/', $windowIndex)) {
        return '';
    }
    $result = tmux_run(['capture-pane', '-p', '-t', $session . ':' . $windowIndex, '-S', '-35']);
    if ($result['code'] !== 0) {
        return '';
    }
    return $result['stdout'];
}

function infer_window_status(string $command, int $copyMode, string $screenText): array {
    $screen = function_exists('mb_strtolower') ? mb_strtolower($screenText, 'UTF-8') : strtolower($screenText);
    $command = trim($command);
    $commandKey = strtolower($command);

    if (preg_match('/\b(approve|approval|allow|deny|permission|escalat)\b/u', $screen)
        || preg_match('/\b(confirm|proceed)\b.{0,40}(\?|\[(y\/n|y\/N|yes\/no)\])/iu', $screenText)
        || preg_match('/(需要|批准|确认|允许).{0,12}(执行|继续|命令|操作)/u', $screen)
        || preg_match('/\[(y\/n|yes\/no|allow|deny)\]/iu', $screenText)) {
        return ['status' => 'needs_approval', 'label' => '需要确认', 'icon' => '!', 'class' => 'needs-approval'];
    }

    if ($copyMode === 1
        || preg_match('/\b(paused|suspended|stopped|press .{0,20} to continue)\b/u', $screen)
        || preg_match('/\[(paused|suspended|stopped)\]/u', $screen)) {
        return ['status' => 'paused', 'label' => '暂停/浏览', 'icon' => 'II', 'class' => 'paused'];
    }

    $idleCommands = ['bash', 'zsh', 'sh', 'fish', 'tmux', 'login', 'sudo', 'su'];
    if ($commandKey !== '' && !in_array($commandKey, $idleCommands, true)) {
        return ['status' => 'running', 'label' => '运行中', 'icon' => '>', 'class' => 'running'];
    }

    return ['status' => 'idle', 'label' => '空闲', 'icon' => '-', 'class' => 'idle'];
}

function current_window_from_display(string $session): ?array {
    $result = tmux_run([
        'display-message',
        '-p',
        '-t',
        $session . ':.',
        '#{window_index}' . "\t" . '#{window_id}' . "\t" . '#{window_name}' . "\t" . '#{?automatic-rename,1,0}',
    ]);
    if ($result['code'] !== 0 || trim($result['stdout']) === '') {
        return null;
    }
    $parts = explode("\t", trim($result['stdout']));
    if (count($parts) < 4) {
        return null;
    }
    return [
        'index' => (int) $parts[0],
        'id' => $parts[1],
        'name' => $parts[2],
        'active' => true,
        'automaticRename' => $parts[3] === '1',
    ];
}

function session_snapshot(string $session): array {
    $windows = list_windows_meta($session);
    $currentWindow = current_window_from_display($session);
    foreach ($windows as $index => $window) {
        $isCurrent = $currentWindow !== null && $window['id'] === $currentWindow['id'];
        if ($isCurrent) {
            $windows[$index]['active'] = true;
            $windows[$index]['name'] = $currentWindow['name'];
            $windows[$index]['automaticRename'] = $currentWindow['automaticRename'];
            $currentWindow = $windows[$index];
            continue;
        }
        if ($currentWindow !== null) {
            $windows[$index]['active'] = false;
            continue;
        }
        if ($window['active']) {
            $currentWindow = $window;
        }
    }
    return [
        'session' => $session,
        'state' => current_state($session),
        'copyMode' => in_copy_mode($session),
        'windows' => $windows,
        'currentWindow' => $currentWindow,
        'currentAlias' => $currentWindow['name'] ?? '',
        'windowLabel' => $currentWindow['name'] ?? '',
    ];
}

function diagnostic_snapshot(string $session): array {
    $nameDisplay = tmux_run(['display-message', '-p', '-t', $session . ':.', '#{window_name}']);
    $nameList = tmux_run([
        'list-windows',
        '-t',
        $session,
        '-F',
        '#{window_index}' . "\t" . '#{window_id}' . "\t" . '#{window_name}' . "\t" . '#{?window_active,1,0}' . "\t" . '#{?automatic-rename,1,0}',
    ]);
    $state = tmux_run(['display-message', '-p', '-t', $session . ':.', '#{session_name} | window #{window_index}:#{window_name} | pane #{pane_index} | #{pane_current_command}']);
    return [
        'phpSapi' => PHP_SAPI,
        'lang' => getenv('LANG') ?: '',
        'lcAll' => getenv('LC_ALL') ?: '',
        'setlocaleCtype' => setlocale(LC_CTYPE, 0) ?: '',
        'displayName' => $nameDisplay,
        'listWindowsRaw' => $nameList,
        'stateRaw' => $state,
        'displayNameBase64' => base64_encode($nameDisplay['stdout'] ?? ''),
        'listWindowsBase64' => base64_encode($nameList['stdout'] ?? ''),
        'stateBase64' => base64_encode($state['stdout'] ?? ''),
        'displayNameHex' => bin2hex($nameDisplay['stdout'] ?? ''),
        'listWindowsHex' => bin2hex($nameList['stdout'] ?? ''),
        'stateHex' => bin2hex($state['stdout'] ?? ''),
        'probeChinese' => '网页优化探针',
        'probeChineseBase64' => base64_encode('网页优化探针'),
        'probeChineseHex' => bin2hex('网页优化探针'),
    ];
}

function session_check(string $session): array {
    $result = tmux_run(['has-session', '-t', $session]);
    return [
        'ok' => $result['code'] === 0,
        'stderr' => $result['stderr'],
        'stdout' => $result['stdout'],
        'code' => $result['code'],
    ];
}

function run_tmux_or_noop(array $command, array $acceptableErrors = []): array {
    $result = tmux_run($command);
    if ($result['code'] === 0) {
        return ['ok' => true, 'noop' => false, 'error' => ''];
    }
    foreach ($acceptableErrors as $fragment) {
        if ($fragment !== '' && stripos($result['stderr'], $fragment) !== false) {
            return ['ok' => true, 'noop' => true, 'error' => $result['stderr']];
        }
    }
    return ['ok' => false, 'noop' => false, 'error' => $result['stderr'] !== '' ? $result['stderr'] : 'tmux command failed'];
}

function in_copy_mode(string $session): bool {
    $result = tmux_run(['display-message', '-p', '-t', $session . ':.', '#{pane_in_mode}']);
    return $result['code'] === 0 && trim($result['stdout']) === '1';
}

function exit_copy_mode(string $session): array {
    if (!in_copy_mode($session)) {
        return ['ok' => true, 'noop' => true, 'error' => ''];
    }
    $result = run_tmux_or_noop(['send-keys', '-X', '-t', $session . ':.', 'cancel']);
    if (!$result['ok'] || !in_copy_mode($session)) {
        return $result;
    }
    return run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Escape']);
}

function payload(string $session, string $label, bool $noop = false, ?string $note = null): array {
    return array_merge([
        'ok' => true,
        'label' => $label,
        'noop' => $noop,
        'note' => $note,
    ], session_snapshot($session));
}

function copy_mode_scroll(string $session, string $direction): array {
    if (!in_copy_mode($session)) {
        return ['ok' => true, 'noop' => true, 'error' => 'copy mode required'];
    }
    $key = $direction === 'up' ? 'scroll-up' : 'scroll-down';
    return run_tmux_or_noop(['send-keys', '-X', '-t', $session . ':.', $key]);
}

function copy_mode_page(string $session, string $direction): array {
    if (!in_copy_mode($session)) {
        return ['ok' => true, 'noop' => true, 'error' => 'copy mode required'];
    }
    $key = $direction === 'up' ? 'page-up' : 'page-down';
    return run_tmux_or_noop(['send-keys', '-X', '-t', $session . ':.', $key]);
}

function send_text_to_tmux(string $session, string $text): array {
    if ($text === '') {
        return ['ok' => true, 'noop' => true, 'error' => ''];
    }
    if (strlen($text) > 20000) {
        return ['ok' => false, 'noop' => false, 'error' => 'text too long'];
    }
    $buffer = 'ops-paste-' . bin2hex(random_bytes(4));
    $set = tmux_run(['set-buffer', '-b', $buffer, $text]);
    if ($set['code'] !== 0) {
        return ['ok' => false, 'noop' => false, 'error' => $set['stderr'] !== '' ? $set['stderr'] : 'failed to set tmux buffer'];
    }
    $paste = tmux_run(['paste-buffer', '-d', '-p', '-b', $buffer, '-t', $session . ':.']);
    if ($paste['code'] !== 0) {
        return ['ok' => false, 'noop' => false, 'error' => $paste['stderr'] !== '' ? $paste['stderr'] : 'failed to paste tmux buffer'];
    }
    return ['ok' => true, 'noop' => false, 'error' => ''];
}

function latest_tmux_buffer(): array {
    $list = tmux_run(['list-buffers', '-F', '#{buffer_name}' . "\t" . '#{buffer_size}']);
    if ($list['code'] !== 0) {
        return ['ok' => false, 'error' => $list['stderr'] !== '' ? $list['stderr'] : 'failed to list tmux buffers'];
    }
    $line = strtok($list['stdout'], "\n");
    $line = $line === false ? '' : trim($line);
    if ($line === '') {
        return ['ok' => true, 'bufferName' => '', 'bufferSize' => 0, 'bufferText' => ''];
    }
    $parts = explode("\t", $line);
    $bufferName = $parts[0] ?? '';
    $bufferSize = isset($parts[1]) ? (int) $parts[1] : 0;
    if ($bufferName === '') {
        return ['ok' => true, 'bufferName' => '', 'bufferSize' => 0, 'bufferText' => ''];
    }
    $show = tmux_run(['show-buffer', '-b', $bufferName]);
    if ($show['code'] !== 0) {
        return ['ok' => false, 'error' => $show['stderr'] !== '' ? $show['stderr'] : 'failed to read tmux buffer'];
    }
    return ['ok' => true, 'bufferName' => $bufferName, 'bufferSize' => $bufferSize, 'bufferText' => $show['stdout']];
}

$rawInput = file_get_contents('php://input');
if ($rawInput === '' && PHP_SAPI === 'cli') {
    $rawInput = stream_get_contents(STDIN);
}
$input = json_decode($rawInput, true);
$requestMethod = $_SERVER['REQUEST_METHOD'] ?? 'GET';
$session = sanitize_session($_GET['session'] ?? ($input['session'] ?? 'webcli'));

$sessionCheck = session_check($session);
if (!$sessionCheck['ok']) {
    $detail = $sessionCheck['stderr'] !== '' ? $sessionCheck['stderr'] : 'tmux session not found';
    respond(404, ['ok' => false, 'error' => 'tmux session not found', 'detail' => $detail, 'session' => $session]);
}

if ($requestMethod === 'GET' && isset($_GET['state'])) {
    $payload = array_merge(['ok' => true], session_snapshot($session));
    if (isset($_GET['diag'])) {
        $payload['diag'] = diagnostic_snapshot($session);
    }
    respond(200, $payload);
}

if ($requestMethod !== 'POST') {
    respond(405, ['ok' => false, 'error' => 'Only POST is allowed']);
}

$action = is_array($input) ? ($input['action'] ?? '') : '';
$text = is_array($input) ? (string) ($input['text'] ?? '') : '';
$alias = is_array($input) ? ($input['alias'] ?? null) : null;
$window = is_array($input) ? ($input['window'] ?? null) : null;
$note = null;

switch ($action) {
    case 'pane_left':
        $result = run_tmux_or_noop(['select-pane', '-L', '-t', $session . ':.'], ['no pane']);
        break;
    case 'pane_right':
        $result = run_tmux_or_noop(['select-pane', '-R', '-t', $session . ':.'], ['no pane']);
        break;
    case 'pane_up':
        $result = run_tmux_or_noop(['select-pane', '-U', '-t', $session . ':.'], ['no pane']);
        break;
    case 'pane_down':
        $result = run_tmux_or_noop(['select-pane', '-D', '-t', $session . ':.'], ['no pane']);
        break;
    case 'pane_next':
        $result = run_tmux_or_noop(['select-pane', '-t', $session . ':.+']);
        break;
    case 'pane_zoom':
        $result = run_tmux_or_noop(['resize-pane', '-Z', '-t', $session . ':.']);
        break;
    case 'window_prev':
        $result = run_tmux_or_noop(['previous-window', '-t', $session], ['no last window']);
        break;
    case 'window_next':
        $result = run_tmux_or_noop(['next-window', '-t', $session], ['no next window']);
        break;
    case 'window_new':
        $result = run_tmux_or_noop(['new-window', '-t', $session]);
        break;
    case 'window_focus':
        $targetWindow = sanitize_window_index((string) $window);
        $result = run_tmux_or_noop(['select-window', '-t', $session . ':' . $targetWindow], ['can\'t find window']);
        if ($result['noop']) {
            $note = '目标窗口不存在，已保持原状';
        }
        break;
    case 'window_alias_set':
        $targetAlias = sanitize_alias($alias);
        $autoRename = run_tmux_or_noop(['set-option', '-w', '-t', $session . ':.', 'automatic-rename', 'off']);
        if (!$autoRename['ok']) {
            $result = $autoRename;
            break;
        }
        $result = run_tmux_or_noop(['rename-window', '-t', $session . ':.', $targetAlias]);
        if ($result['ok']) {
            $note = '已保存当前窗口备注';
        }
        break;
    case 'clipboard_buffer_latest':
        $buffer = latest_tmux_buffer();
        if (!$buffer['ok']) {
            respond(500, ['ok' => false, 'error' => $buffer['error'], 'session' => $session]);
        }
        respond(200, array_merge(['ok' => true, 'session' => $session], $buffer));
    case 'split_h':
        $result = run_tmux_or_noop(['split-window', '-h', '-t', $session . ':.']);
        break;
    case 'split_v':
        $result = run_tmux_or_noop(['split-window', '-v', '-t', $session . ':.']);
        break;
    case 'layout_tiled':
        $result = run_tmux_or_noop(['select-layout', '-t', $session, 'tiled']);
        break;
    case 'layout_even_h':
        $result = run_tmux_or_noop(['select-layout', '-t', $session, 'even-horizontal']);
        break;
    case 'layout_even_v':
        $result = run_tmux_or_noop(['select-layout', '-t', $session, 'even-vertical']);
        break;
    case 'copy_mode':
        $result = run_tmux_or_noop(['copy-mode', '-t', $session . ':.']);
        break;
    case 'copy_mode_toggle':
        if (in_copy_mode($session)) {
            $result = exit_copy_mode($session);
            $note = '已退出复制模式，可以继续输入';
        } else {
            $result = run_tmux_or_noop(['copy-mode', '-t', $session . ':.']);
            $note = '已进入复制模式；再次点击同一个按钮可退出';
        }
        break;
    case 'page_up':
        $result = copy_mode_page($session, 'up');
        if ($result['noop']) {
            $note = '请先进入复制模式，再使用 PgUp';
        }
        break;
    case 'page_down':
        $result = copy_mode_page($session, 'down');
        if ($result['noop']) {
            $note = '请先进入复制模式，再使用 PgDn';
        }
        break;
    case 'scroll_up':
        $result = copy_mode_scroll($session, 'up');
        if ($result['noop']) {
            $note = '请先进入复制模式，再使用上滚';
        }
        break;
    case 'scroll_down':
        $result = copy_mode_scroll($session, 'down');
        if ($result['noop']) {
            $note = '请先进入复制模式，再使用下滚';
        }
        break;
    case 'enter':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Enter']);
        break;
    case 'escape':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Escape']);
        break;
    case 'copy_mode_exit':
        $result = exit_copy_mode($session);
        if ($result['ok']) {
            $note = $result['noop'] ? '当前不在复制模式' : '已退出复制模式，可以继续输入';
        }
        break;
    case 'send_text':
        $result = send_text_to_tmux($session, $text);
        break;
    case 'tab':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Tab']);
        break;
    case 'arrow_up':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Up']);
        break;
    case 'arrow_down':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Down']);
        break;
    case 'arrow_left':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Left']);
        break;
    case 'arrow_right':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Right']);
        break;
    case 'home':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'Home']);
        break;
    case 'end':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'End']);
        break;
    case 'backspace':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'BSpace']);
        break;
    case 'delete':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'DC']);
        break;
    case 'ctrl_a':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-a']);
        break;
    case 'ctrl_b':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-b']);
        break;
    case 'ctrl_e':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-e']);
        break;
    case 'ctrl_l':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-l']);
        break;
    case 'ctrl_r':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-r']);
        break;
    case 'ctrl_u':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-u']);
        break;
    case 'ctrl_k':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-k']);
        break;
    case 'ctrl_w':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-w']);
        break;
    case 'ctrl_d':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-d']);
        break;
    case 'ctrl_z':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-z']);
        break;
    case 'ctrl_c':
        $result = run_tmux_or_noop(['send-keys', '-t', $session . ':.', 'C-c']);
        break;
    case 'close_current':
        $paneCount = tmux_run(['display-message', '-p', '-t', $session . ':.', '#{window_panes}']);
        if ($paneCount['code'] !== 0) {
            respond(500, ['ok' => false, 'error' => $paneCount['stderr'] !== '' ? $paneCount['stderr'] : 'failed to inspect panes', 'session' => $session]);
        }
        if ((int) trim($paneCount['stdout']) > 1) {
            $result = run_tmux_or_noop(['kill-pane', '-t', $session . ':.']);
            break;
        }
        $windowCount = tmux_run(['list-windows', '-t', $session]);
        if ($windowCount['code'] !== 0) {
            respond(500, ['ok' => false, 'error' => $windowCount['stderr'] !== '' ? $windowCount['stderr'] : 'failed to inspect windows', 'session' => $session]);
        }
        $count = substr_count(trim($windowCount['stdout']), "\n") + (trim($windowCount['stdout']) === '' ? 0 : 1);
        if ($count > 1) {
            $result = run_tmux_or_noop(['kill-window', '-t', $session . ':.']);
            break;
        }
        $result = ['ok' => true, 'noop' => true, 'error' => ''];
        break;
    default:
        respond(400, ['ok' => false, 'error' => 'Unknown action']);
}

$labels = [
    'pane_left' => '切到左侧 pane',
    'pane_right' => '切到右侧 pane',
    'pane_up' => '切到上方 pane',
    'pane_down' => '切到下方 pane',
    'pane_next' => '切到下一个 pane',
    'pane_zoom' => '切换 pane 放大',
    'window_prev' => '切到上一窗口',
    'window_next' => '切到下一窗口',
    'window_new' => '新建窗口',
    'window_focus' => '切到指定窗口',
    'window_alias_set' => '保存窗口备注',
    'clipboard_buffer_latest' => '读取 tmux 最新缓冲区',
    'split_h' => '左右分屏',
    'split_v' => '上下分屏',
    'layout_tiled' => '平铺布局',
    'layout_even_h' => '横向均分',
    'layout_even_v' => '纵向均分',
    'copy_mode' => '进入复制模式',
    'copy_mode_toggle' => '切换复制模式',
    'page_up' => '向上翻页',
    'page_down' => '向下翻页',
    'scroll_up' => '向上滚动',
    'scroll_down' => '向下滚动',
    'enter' => '发送 Enter',
    'escape' => '发送 Esc',
    'copy_mode_exit' => '退出复制模式',
    'send_text' => '发送粘贴文本',
    'tab' => '发送 Tab',
    'arrow_up' => '发送 ↑',
    'arrow_down' => '发送 ↓',
    'arrow_left' => '发送 ←',
    'arrow_right' => '发送 →',
    'home' => '发送 Home',
    'end' => '发送 End',
    'backspace' => '发送 Backspace',
    'delete' => '发送 Delete',
    'ctrl_a' => '发送 Ctrl-A',
    'ctrl_b' => '发送 Ctrl-B',
    'ctrl_e' => '发送 Ctrl-E',
    'ctrl_l' => '发送 Ctrl-L',
    'ctrl_r' => '发送 Ctrl-R',
    'ctrl_u' => '发送 Ctrl-U',
    'ctrl_k' => '发送 Ctrl-K',
    'ctrl_w' => '发送 Ctrl-W',
    'ctrl_d' => '发送 Ctrl-D',
    'ctrl_z' => '发送 Ctrl-Z',
    'ctrl_c' => '发送 Ctrl-C',
    'close_current' => '关闭当前对话',
];

if (!$result['ok']) {
    respond(500, [
        'ok' => false,
        'error' => $result['error'],
        'label' => $labels[$action] ?? $action,
        'session' => $session,
    ]);
}

respond(200, payload(
    $session,
    $labels[$action] ?? $action,
    $result['noop'],
    $note ?? ($result['noop'] ? (($action === 'close_current') ? '最后一个 pane/window 不自动关闭，避免把整个终端关掉' : '当前没有可切换的目标，已保持原状') : null),
));
