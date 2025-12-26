from flask import Flask, render_template, request, jsonify, session, redirect, url_for, render_template_string
import subprocess, os, signal, time, psutil, logging, requests, threading
from werkzeug.utils import secure_filename

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, template_folder='.')
app.secret_key = "BEAMMP_NEON_V12_8_FINAL"

# File Paths
SERVER_FILE = "BeamMP-Server.ubuntu.24.04.x86_64"
CONFIG_FILE = "ServerConfig.toml"
LOG_FILE = "server.log"
PASSWORD_FILE = "pass.txt"
AUTOSTART_FILE = "autostart.txt"
RESOURCE_DIR = "Resources"
CLIENT_MODS = os.path.join(RESOURCE_DIR, "Client")
SERVER_MODS = os.path.join(RESOURCE_DIR, "Server")
UPDATE_URL = "https://github.com/BeamMP/BeamMP-Server/releases/latest/download/BeamMP-Server.ubuntu.24.04.x86_64"

update_stats = {"status": "idle", "percent": 0, "speed": "0 MB/s"}

def write_log(msg, clear=True):
    with open(LOG_FILE, "w" if clear else "a") as f:
        f.write(f"--- {msg} ---\n")

for folder in [CLIENT_MODS, SERVER_MODS]:
    os.makedirs(folder, exist_ok=True)

def is_running():
    return any("BeamMP-Server" in p.info['name'] for p in psutil.process_iter(['name']))

def kill_srv():
    for p in psutil.process_iter(['name']):
        if "BeamMP-Server" in p.info['name']:
            try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except: p.kill()
    time.sleep(1)

def check_autostart():
    if os.path.exists(AUTOSTART_FILE):
        with open(AUTOSTART_FILE, "r") as f:
            if f.read().strip() == "true":
                write_log("AUTOSTART INITIATED", clear=True)
                subprocess.Popen([f"./{SERVER_FILE}"], stdout=open(LOG_FILE, "a"), stderr=open(LOG_FILE, "a"), preexec_fn=os.setsid)

@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    content = open(CONFIG_FILE, 'r').read() if os.path.exists(CONFIG_FILE) else ""
    autostart_enabled = "false"
    if os.path.exists(AUTOSTART_FILE):
        with open(AUTOSTART_FILE, "r") as f: autostart_enabled = f.read().strip()
    return render_template('index.html', info=content, autostart=autostart_enabled)

@app.route('/toggle_autostart', methods=['POST'])
def toggle_autostart():
    state = request.json.get('state')
    with open(AUTOSTART_FILE, "w") as f: f.write(state)
    return jsonify({"status": "saved"})

@app.route('/stats')
def get_stats():
    ignore = ['mods.json', '.DS_Store']
    return jsonify({
        "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent,
        "status": "ONLINE" if is_running() else "OFFLINE",
        "client_mods": [f for f in os.listdir(CLIENT_MODS) if f not in ignore],
        "server_mods": [f for f in os.listdir(SERVER_MODS) if f not in ignore]
    })

@app.route('/action/<cmd>')
def action(cmd):
    if cmd in ["start", "restart"]:
        write_log(f"SERVER {cmd.upper()}ING", clear=True)
        kill_srv()
        subprocess.Popen([f"./{SERVER_FILE}"], stdout=open(LOG_FILE, "a"), stderr=open(LOG_FILE, "a"), preexec_fn=os.setsid)
    elif cmd == "stop":
        kill_srv()
        write_log("SERVER STOPPED", clear=True)
    return jsonify({"status": "ok"})

@app.route('/save', methods=['POST'])
def save():
    with open(CONFIG_FILE, 'w') as f: f.write(request.form.get('config_data'))
    return jsonify({"is_running": is_running()})

@app.route('/upload', methods=['POST'])
def upload():
    target = request.form.get('target')
    file = request.files['file']
    file.save(os.path.join(CLIENT_MODS if target == 'Client' else SERVER_MODS, secure_filename(file.filename)))
    return jsonify({"needs_restart": is_running()})

@app.route('/delete_mod', methods=['POST'])
def delete_mod():
    data = request.json
    path = os.path.join(CLIENT_MODS if data['target'] == 'Client' else SERVER_MODS, secure_filename(data['filename']))
    if os.path.exists(path): os.remove(path)
    return jsonify({"ok": True})

@app.route('/factory_reset', methods=['POST'])
def reset():
    kill_srv()
    if os.path.exists(PASSWORD_FILE): os.remove(PASSWORD_FILE)
    if os.path.exists(AUTOSTART_FILE): os.remove(AUTOSTART_FILE)
    session.clear()
    return jsonify({"ok": True})

@app.route('/shutdown_panel', methods=['POST'])
def shutdown_panel():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({"ok": True})

@app.route('/update_server', methods=['POST'])
def update():
    def run():
        global update_stats
        update_stats = {"status": "downloading", "percent": 0, "speed": "0 MB/s"}
        r = requests.get(UPDATE_URL, stream=True)
        total = int(r.headers.get('content-length', 0))
        dl, start = 0, time.time()
        with open(SERVER_FILE, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk); dl += len(chunk)
                update_stats["percent"] = int((dl/total)*100)
                update_stats["speed"] = f"{(dl/1024/1024)/(max(time.time()-start, 1)):.2f} MB/s"
        os.chmod(SERVER_FILE, 0o755)
        update_stats["status"] = "success"
    threading.Thread(target=run).start()
    return jsonify({"ok": True})

@app.route('/update_status')
def up_stat(): return jsonify(update_stats)

@app.route('/console')
def console():
    return "".join(open(LOG_FILE, "r").readlines()[-30:]) if os.path.exists(LOG_FILE) else ""

# --- LOGIN & SETUP WITH GITHUB LINK ---
LOGIN_HTML = '''
<body style="background:#050508;color:#00f2ff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Orbitron',sans-serif;margin:0;">
    <form method="post" style="background:rgba(255,255,255,0.03);padding:50px;border-radius:20px;border:1px solid rgba(255,255,255,0.1);text-align:center;backdrop-filter:blur(10px);width:300px;">
        <h1 style="font-size:1.2rem;letter-spacing:3px;margin-bottom:30px;">{{title}}</h1>
        <input type="password" name="password" placeholder="PASSWORD" style="background:#000;border:1px solid #333;color:#fff;padding:12px;border-radius:8px;width:100%;text-align:center;outline:none;font-family:sans-serif;" autofocus>
        <br><br>
        <button type="submit" style="background:#00f2ff;border:none;padding:12px 30px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;letter-spacing:1px;transition:0.3s;">ENTER</button>
        <hr style="border:0;border-top:1px solid rgba(255,255,255,0.05);margin:25px 0;">
        <a href="https://github.com/YOUR_USERNAME" target="_blank" style="color:rgba(255,255,255,0.3);text-decoration:none;font-size:10px;letter-spacing:1px;transition:0.3s;" onmouseover="this.style.color='#00f2ff'" onmouseout="this.style.color='rgba(255,255,255,0.3)'">GITHUB PROFILE</a>
    </form>
</body>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not os.path.exists(PASSWORD_FILE): return redirect(url_for('setup'))
    if request.method == 'POST':
        if request.form.get('password') == open(PASSWORD_FILE, "r").read().strip():
            session['logged_in'] = True; return redirect(url_for('index'))
    return render_template_string(LOGIN_HTML, title="LOGIN")

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        with open(PASSWORD_FILE, "w") as f: f.write(request.form.get('password'))
        return redirect(url_for('login'))
    return render_template_string(LOGIN_HTML, title="CREATE PASSWORD")

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    check_autostart()
    app.run(host='0.0.0.0', port=5000)
