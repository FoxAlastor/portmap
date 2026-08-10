import socket
import concurrent.futures
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import platform
import time

app = Flask(__name__)
CORS(app)

COMMON_PORTS = {
    20: "FTP Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    465: "SMTPS", 587: "SMTP TLS", 993: "IMAPS", 995: "POP3S",
    3000: "Node/React Dev", 3306: "MySQL", 3389: "RDP", 4200: "Angular Dev",
    5000: "Flask/Dev", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    6443: "K8s API", 7000: "Cassandra", 8000: "HTTP Alt", 8080: "HTTP Proxy",
    8081: "HTTP Alt", 8082: "HTTP Alt", 8083: "HTTP Alt", 8088: "HTTP Alt",
    8090: "HTTP Alt", 8443: "HTTPS Alt", 8888: "Jupyter", 9000: "PHP-FPM",
    9090: "Prometheus", 9200: "Elasticsearch", 9300: "Elasticsearch Cluster",
    27017: "MongoDB", 27018: "MongoDB", 28017: "MongoDB Web",
    5601: "Kibana", 4369: "RabbitMQ EPM", 5672: "RabbitMQ", 15672: "RabbitMQ Mgmt",
    2181: "Zookeeper", 2375: "Docker", 2376: "Docker TLS",
    1433: "MSSQL", 1521: "Oracle DB", 5984: "CouchDB",
    6000: "X11", 6001: "X11", 11211: "Memcached",
    4000: "Dev", 4001: "Dev", 4002: "Dev", 4003: "Dev",
    7070: "Dev", 7080: "Dev", 7443: "Dev",
    10000: "Webmin", 10080: "HTTP Alt", 10443: "HTTPS Alt",
}

def check_port(host, port, timeout=0.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return {"port": port, "status": "open", "service": COMMON_PORTS.get(port, "Unknown")}
        else:
            return {"port": port, "status": "closed", "service": COMMON_PORTS.get(port, "Unknown")}
    except Exception as e:
        return {"port": port, "status": "error", "service": COMMON_PORTS.get(port, "Unknown"), "error": str(e)}

def ping_host(host):
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", "-W", "1", host]
        result = subprocess.run(command, capture_output=True, timeout=3)
        return result.returncode == 0
    except Exception:
        try:
            socket.setdefaulttimeout(2)
            socket.gethostbyname(host)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, 80))
            sock.close()
            return True
        except:
            return False

@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json
    host = data.get("host", "localhost")
    port_range = data.get("range", "common")
    custom_ports = data.get("ports", [])
    timeout = float(data.get("timeout", 0.5))

    # Resolve hostname
    try:
        resolved_ip = socket.gethostbyname(host)
    except Exception:
        return jsonify({"error": f"Cannot resolve host: {host}"}), 400

    # Determine ports to scan
    if port_range == "common":
        ports = list(COMMON_PORTS.keys())
    elif port_range == "custom" and custom_ports:
        ports = [int(p) for p in custom_ports if str(p).isdigit()]
    elif port_range == "range":
        start = int(data.get("start", 1))
        end = int(data.get("end", 1024))
        start = max(1, min(start, 65535))
        end = max(start, min(end, 65535))
        ports = list(range(start, end + 1))
    else:
        ports = list(COMMON_PORTS.keys())

    start_time = time.time()

    # Check host reachability
    alive = ping_host(resolved_ip)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = {executor.submit(check_port, resolved_ip, port, timeout): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda x: x["port"])
    elapsed = round(time.time() - start_time, 2)

    open_ports = [r for r in results if r["status"] == "open"]
    closed_ports = [r for r in results if r["status"] == "closed"]

    return jsonify({
        "host": host,
        "ip": resolved_ip,
        "alive": alive,
        "scanned": len(ports),
        "open": len(open_ports),
        "closed": len(closed_ports),
        "elapsed": elapsed,
        "results": results,
        "open_ports": open_ports,
    })

@app.route("/api/ping", methods=["POST"])
def ping():
    data = request.json
    host = data.get("host", "localhost")
    try:
        ip = socket.gethostbyname(host)
        alive = ping_host(ip)
        return jsonify({"host": host, "ip": ip, "alive": alive})
    except Exception as e:
        return jsonify({"host": host, "alive": False, "error": str(e)})

@app.route("/api/local", methods=["GET"])
def local_info():
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    return jsonify({"hostname": hostname, "local_ip": local_ip})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
