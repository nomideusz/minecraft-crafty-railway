#!/usr/bin/env python3
"""First boot: create a Paper server in Crafty on port 25565 (where Railway's TCP proxy
points), with a heap sized to this plan, nightly backups, and start it."""
import json, os, re, ssl, time, urllib.request, zipfile

API = "https://127.0.0.1:8443/api/v2"
TLS = ssl._create_unverified_context()  # Crafty's self-signed cert, on localhost
DONE = "/data/config/.first-server-done"
token = None


def api(method, path, body=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}"} if token else {})
    with urllib.request.urlopen(req, context=TLS, timeout=60) as r:
        return json.load(r)


for _ in range(60):  # Crafty builds its database and its list of server jars on first start
    try:
        token = api("POST", "/auth/login", {"username": "admin", "password": os.environ["CRAFTY_ADMIN_PASSWORD"]})["data"]["token"]
        jars = json.load(open("/data/config/bigbucket.json"))["categories"]
        break
    except (OSError, ValueError):
        time.sleep(5)
else:
    raise SystemExit("first-server: could not log in to Crafty as admin with CRAFTY_ADMIN_PASSWORD")

# The admin exists now; the seed file holds its password in plain text.
for f in ("default.json", "default-creds.txt"):
    if os.path.exists(f"/data/config/{f}"):
        os.remove(f"/data/config/{f}")

if api("GET", "/servers")["data"]:  # from an earlier boot that didn't finish, or made in the panel
    open(DONE, "w").close()
    raise SystemExit(0)

if os.environ.get("EULA", "").strip().lower() != "true":
    raise SystemExit("first-server: no Minecraft server yet - set EULA=TRUE to accept the "
                     "Minecraft EULA (https://aka.ms/MinecraftEULA) and redeploy")

versions = jars["mc_java_servers"]["types"]["paper"]["versions"]
version = max((v for v in versions if re.fullmatch(r"[\d.]+", v)), key=lambda v: [int(x) for x in v.split(".")])

# Heap: the plan's memory minus ~1 GB for the JVM itself and Crafty, 1-4 GB. Below
# ~2 GB Paper gets OOM-killed and crash detection restarts it forever.
limit = open("/sys/fs/cgroup/memory.max").read().strip()
if limit != "max" and int(limit) < 1.5 * 2**30:
    raise SystemExit(f"first-server: no Minecraft server yet - it needs 2 GB of memory and this service "
                     f"gets {int(limit) // 2**20} MB; move to the Hobby plan or above and redeploy")
heap = 4 if limit == "max" else max(1, min(4, int(limit) // 2**30 - 1))

sid = api("POST", "/servers", {
    "name": "Minecraft",
    "monitoring_type": "minecraft_java",
    "minecraft_java_monitoring_data": {"host": "127.0.0.1", "port": 25565},
    "create_type": "minecraft_java",
    "minecraft_java_create_data": {"create_type": "download_jar", "download_jar_create_data": {
        "category": "mc_java_servers", "type": "paper", "version": version,
        "mem_min": 1, "mem_max": heap, "server_properties_port": 25565, "agree_to_eula": True}},
})["data"]["new_server_id"]
# Crafty ignores these on create. Autostart brings the server back after every redeploy.
api("PATCH", f"/servers/{sid}", {"auto_start": True, "crash_detection": True})

# Crafty's default backup keeps every copy forever: keep 3, taken nightly, without
# the ~150 MB Paper downloads again on start (the panel lists exclusions as full paths).
backup_id = next(iter(api("GET", f"/servers/{sid}/backups")))
api("PATCH", f"/servers/{sid}/backups/backup/{backup_id}", {"max_backups": 3, "excluded_dirs": [
    f"/data/servers/{sid}/{d}" for d in ("cache", "libraries", "versions")]})
api("POST", f"/servers/{sid}/tasks", {  # every field, as the panel sends it: Crafty has no defaults
    "name": "Nightly backup", "enabled": True, "action": "backup", "command": "backup_server",
    "action_id": backup_id, "interval": 1, "interval_type": "days", "start_time": "04:00",
    "cron_string": "", "one_time": False, "parent": None, "delay": 0})
open(DONE, "w").close()
print(f"first-server: created Paper {version} with a {heap} GB heap, backups nightly at 04:00 UTC", flush=True)

# Crafty downloads the jar in the background; it reads as a zip only once complete.
for _ in range(120):
    time.sleep(5)
    if zipfile.is_zipfile(f"/data/servers/{sid}/paper.jar"):
        break
else:
    raise SystemExit("first-server: Paper did not finish downloading - start the server in the panel later")
api("POST", f"/servers/{sid}/action/start_server")
