# import socket
# import threading
# import json
# import time
# from datetime import datetime

# # ================= CONFIG =================
# HOST = "0.0.0.0"       # Listen on all interfaces
# PORT = 5003
# BUFFER_SIZE = 4096
# JSON_FILE = "modem_data.jsonl"
# POLL_INTERVAL = 1      # seconds

# file_lock = threading.Lock()

# print("🔧 Modem Server (NB-IoT SAFE MODE)")
# print("✅ Server restart safe — modem controls reconnect")
# print("🚫 No forced disconnects")

# # ================= LOGGER =================
# def log_json(protocol, addr, data):
#     """Log incoming data to console and JSONL file."""
#     record = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "protocol": protocol,
#         "ip": addr[0],
#         "port": addr[1],
#         "data": data
#     }

#     print(record)

#     with file_lock:
#         with open(JSON_FILE, "a", encoding="utf-8") as f:
#             f.write(json.dumps(record, ensure_ascii=False) + "\n")

# # ================= TCP HANDLER =================
# def handle_tcp(conn, addr):
#     """Handle TCP modem connection with periodic polling."""
#     print(f"🔗 TCP connected: {addr}")
#     conn.settimeout(5)  # avoid blocking forever on recv
#     buffer = ""

#     try:
#         while True:
#             # 1️⃣ Poll modem by sending a request every second
#             try:
#                 conn.sendall(b"STATUS\n")  # <-- replace with modem's actual command
#             except BrokenPipeError:
#                 print(f"⚠ Modem disconnected: {addr}")
#                 break

#             # 2️⃣ Receive any data from modem
#             try:
#                 data = conn.recv(BUFFER_SIZE)
#                 if data:
#                     buffer += data.decode(errors="ignore")
#                     while "\n" in buffer:
#                         line, buffer = buffer.split("\n", 1)
#                         if line.strip():
#                             log_json("TCP", addr, line.strip())
#             except socket.timeout:
#                 # No data received this second — continue polling
#                 pass

#             time.sleep(POLL_INTERVAL)

#     except ConnectionResetError:
#         print(f"⚠ Modem reset connection: {addr}")
#     except Exception as e:
#         print(f"⚠ TCP error {addr}: {e}")
#     finally:
#         conn.close()
#         print(f"❌ TCP disconnected: {addr}")

# # ================= TCP SERVER =================
# def tcp_server():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((HOST, PORT))
#     sock.listen(100)
#     print(f"🚀 TCP listening on {HOST}:{PORT}")

#     while True:
#         conn, addr = sock.accept()
#         threading.Thread(target=handle_tcp, args=(conn, addr), daemon=True).start()

# # ================= MAIN =================
# if __name__ == "__main__":
#     threading.Thread(target=tcp_server, daemon=True).start()
#     print("🛰 Modem server is running...")

#     try:
#         while True:
#             time.sleep(60)
#     except KeyboardInterrupt:
#         print("\n🛑 Server stopped by user")
# import socket
# import threading
# import json
# import time
# from datetime import datetime

# # ================= CONFIG =================
# HOST = "0.0.0.0"
# PORT = 5003
# BUFFER_SIZE = 4096
# JSON_FILE = "modem_data.jsonl"

# file_lock = threading.Lock()

# print("🔧 Modem Server (NB-IoT SAFE MODE)")
# print("✅ Server restart safe — modem controls reconnect")
# print("🚫 No forced disconnects")

# # ================= LOGGER =================
# def log_json(protocol, addr, data):
#     record = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "protocol": protocol,
#         "ip": addr[0],
#         "port": addr[1],
#         "data": data
#     }

#     print(record)

#     with file_lock:
#         with open(JSON_FILE, "a", encoding="utf-8") as f:
#             f.write(json.dumps(record, ensure_ascii=False) + "\n")


# # ================= TCP HANDLER =================
# def handle_tcp(conn, addr):
#     print(f"🔗 TCP connected: {addr}")
#     conn.settimeout(None)  # IMPORTANT: never timeout NB modems

#     try:
#         while True:
#             data = conn.recv(BUFFER_SIZE)

#             # Modem closed connection (NORMAL)
#             if not data:
#                 print(f"ℹ Modem closed connection: {addr}")
#                 break

#             msg = data.decode(errors="ignore").strip()
#             log_json("TCP", addr, msg)

#             # ❌ DO NOT send ACK / PING unless modem protocol requires it
#             # ❌ DO NOT close connection
#             # ❌ DO NOT enforce heartbeat

#     except ConnectionResetError:
#         print(f"⚠ Modem reset connection: {addr}")

#     except Exception as e:
#         print(f"⚠ TCP error {addr}: {e}")

#     finally:
#         conn.close()
#         print(f"❌ TCP disconnected (NORMAL): {addr}")


# # ================= TCP SERVER =================
# def tcp_server():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((HOST, PORT))
#     sock.listen(100)

#     print(f"🚀 TCP listening on {HOST}:{PORT}")

#     while True:
#         conn, addr = sock.accept()
#         threading.Thread(
#             target=handle_tcp,
#             args=(conn, addr),
#             daemon=True
#         ).start()


# # ================= UDP SERVER =================
# def udp_server():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind((HOST, PORT))

#     print(f"🚀 UDP listening on {HOST}:{PORT}")

#     while True:
#         data, addr = sock.recvfrom(BUFFER_SIZE)
#         msg = data.decode(errors="ignore").strip()
#         log_json("UDP", addr, msg)


# # ================= MAIN =================
# if __name__ == "__main__":
#     threading.Thread(target=tcp_server, daemon=True).start()
#     threading.Thread(target=udp_server, daemon=True).start()

#     while True:
#         time.sleep(60)


# import socket
# import threading
# import json
# import time
# from datetime import datetime

# # ================= CONFIG =================
# HOST = "0.0.0.0"
# PORT = 5003
# BUFFER_SIZE = 4096

# DATA_FILE = "modem_data.jsonl"
# DEVICE_FILE = "devices.json"

# file_lock = threading.Lock()
# device_lock = threading.Lock()

# print("🔧 NB-IoT Modem Server")
# print("✅ IMEI Registration + Activation Enabled")

# # ================= LOAD DEVICES =================
# def load_devices():
#     try:
#         with open(DEVICE_FILE, "r") as f:
#             return json.load(f)
#     except:
#         return {}

# def save_devices(devices):
#     with open(DEVICE_FILE, "w") as f:
#         json.dump(devices, f, indent=2)

# devices = load_devices()


# # ================= LOGGER =================
# def log_json(protocol, addr, imei, data):
#     record = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "protocol": protocol,
#         "ip": addr[0],
#         "port": addr[1],
#         "imei": imei,
#         "data": data
#     }

#     print(record)

#     with file_lock:
#         with open(DATA_FILE, "a", encoding="utf-8") as f:
#             f.write(json.dumps(record) + "\n")


# # ================= KEEPALIVE =================
# def enable_keepalive(sock):
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

#     if hasattr(socket, "SIO_KEEPALIVE_VALS"):
#         sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 120000, 30000))
#     else:
#         sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
#         sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
#         sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)


# # ================= IMEI PARSER =================
# def extract_imei(msg):
#     # IMEI format
#     if msg.startswith("IMEI:"):
#         return msg.replace("IMEI:", "").strip()

#     # Data packet contains IMEI (comma separated)
#     parts = msg.split(",")
#     for p in parts:
#         if p.isdigit() and len(p) == 15:
#             return p

#     return None


# # ================= TCP HANDLER =================
# def handle_tcp(conn, addr):
#     print(f"🔗 TCP connected: {addr}")

#     enable_keepalive(conn)
#     conn.settimeout(300)

#     imei = None

#     try:
#         while True:
#             try:
#                 data = conn.recv(BUFFER_SIZE)
#                 if not data:
#                     break

#                 msg = data.decode(errors="ignore").strip()
#                 detected_imei = extract_imei(msg)

#                 # ---------------- REGISTER / ACTIVATE ----------------
#                 if detected_imei:
#                     imei = detected_imei

#                     with device_lock:
#                         if imei not in devices:
#                             devices[imei] = {
#                                 "activated": True,
#                                 "first_seen": datetime.now().isoformat(),
#                                 "last_seen": datetime.now().isoformat()
#                             }
#                             save_devices(devices)
#                             print(f"✅ IMEI REGISTERED & ACTIVATED: {imei}")
#                         else:
#                             devices[imei]["last_seen"] = datetime.now().isoformat()
#                             save_devices(devices)

#                 # ---------------- VALIDATE ----------------
#                 if not imei or imei not in devices:
#                     print(f"🚫 Unregistered device from {addr}")
#                     continue

#                 if not devices[imei]["activated"]:
#                     print(f"⛔ IMEI NOT ACTIVE: {imei}")
#                     continue

#                 # ---------------- LOG DATA ----------------
#                 log_json("TCP", addr, imei, msg)

#             except socket.timeout:
#                 continue

#     except Exception as e:
#         print(f"⚠ TCP error {addr}: {e}")

#     finally:
#         try:
#             conn.close()
#         except:
#             pass
#         print(f"❌ TCP disconnected: {addr}")


# # ================= TCP SERVER =================
# def tcp_server():
#     while True:
#         try:
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#             sock.bind((HOST, PORT))
#             sock.listen(100)

#             print(f"🚀 TCP listening on {HOST}:{PORT}")

#             while True:
#                 conn, addr = sock.accept()
#                 threading.Thread(
#                     target=handle_tcp,
#                     args=(conn, addr),
#                     daemon=True
#                 ).start()

#         except Exception as e:
#             print(f"🔥 TCP server restart: {e}")
#             time.sleep(2)


# # ================= MAIN =================
# if __name__ == "__main__":
#     tcp_server()




# # linux code 
# import socket
# import threading
# import json
# from datetime import datetime

# # ================= CONFIG =================
# HOST = "0.0.0.0"
# PORT = 5003
# BUFFER_SIZE = 4096

# DATA_FILE = "modem_data.jsonl"
# DEVICE_FILE = "devices.json"

# file_lock = threading.Lock()
# device_lock = threading.Lock()

# # Cache for reconnects (IP → IMEI)
# ip_imei_cache = {}

# print("🐧 NB-IoT Modem TCP Server (Linux)")
# print("✅ Continuous IMEI Monitoring")
# print("✅ Reconnect Safe")
# print("🚀 Ready")

# # ================= DEVICE DB =================
# def load_devices():
#     try:
#         with open(DEVICE_FILE, "r") as f:
#             return json.load(f)
#     except:
#         return {}

# def save_devices(devices):
#     with open(DEVICE_FILE, "w") as f:
#         json.dump(devices, f, indent=2)

# devices = load_devices()

# # ================= LOGGER =================
# def log_json(protocol, addr, imei, raw_bytes):
#     record = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "protocol": protocol,
#         "ip": addr[0],
#         "port": addr[1],
#         "imei": imei,
#         "data_text": raw_bytes.decode(errors="ignore"),
#         "data_hex": raw_bytes.hex()
#     }

#     print(record)

#     with file_lock:
#         with open(DATA_FILE, "a", encoding="utf-8") as f:
#             f.write(json.dumps(record) + "\n")

# # ================= TCP KEEPALIVE =================
# def enable_keepalive(sock):
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

# # ================= IMEI PARSER =================
# def extract_imei(msg):
#     if msg.startswith("IMEI:"):
#         return msg.replace("IMEI:", "").strip()

#     for part in msg.split(","):
#         if part.isdigit() and len(part) == 15:
#             return part
#     return None

# # ================= TCP HANDLER =================
# def handle_tcp(conn, addr):
#     print(f"🔗 TCP connected: {addr}")

#     enable_keepalive(conn)
#     conn.settimeout(300)  # NB-IoT sleep allowed

#     imei = None

#     try:
#         while True:
#             try:
#                 data = conn.recv(BUFFER_SIZE)

#                 if not data:
#                     print(f"🔌 Modem disconnected normally: {addr}")
#                     break

#                 msg = data.decode(errors="ignore")
#                 detected_imei = extract_imei(msg)

#                 # ----- IMEI DETECTION / CACHE -----
#                 if detected_imei:
#                     imei = detected_imei
#                     ip_imei_cache[addr[0]] = imei

#                     with device_lock:
#                         if imei not in devices:
#                             devices[imei] = {
#                                 "activated": True,
#                                 "first_seen": datetime.now().isoformat(),
#                                 "last_seen": datetime.now().isoformat()
#                             }
#                             save_devices(devices)
#                             print(f"✅ IMEI REGISTERED: {imei}")
#                         else:
#                             devices[imei]["last_seen"] = datetime.now().isoformat()
#                             save_devices(devices)

#                 elif addr[0] in ip_imei_cache:
#                     imei = ip_imei_cache[addr[0]]

#                 # ----- VALIDATION -----
#                 if not imei or imei not in devices or not devices[imei]["activated"]:
#                     continue

#                 # ----- LOG DATA -----
#                 log_json("TCP", addr, imei, data)

#             except socket.timeout:
#                 # Normal NB-IoT sleep
#                 continue

#     except Exception as e:
#         print(f"⚠ TCP error {addr}: {e}")

#     finally:
#         conn.close()
#         print(f"❌ TCP session closed: {addr}")

# # ================= TCP SERVER =================
# def tcp_server():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((HOST, PORT))
#     sock.listen(200)

#     print(f"🚀 TCP listening on {HOST}:{PORT}")

#     while True:
#         conn, addr = sock.accept()
#         threading.Thread(
#             target=handle_tcp,
#             args=(conn, addr),
#             daemon=True
#         ).start()

# # ================= MAIN =================
# if __name__ == "__main__":
#     tcp_server()

# import socket
# import threading
# import json
# from datetime import datetime

# # ================= CONFIG =================
# HOST = "0.0.0.0"
# PORT = 5003
# BUFFER_SIZE = 4096

# DATA_FILE = "modem_data.jsonl"
# DEVICE_FILE = "devices.json"

# file_lock = threading.Lock()
# device_lock = threading.Lock()

# # Cache for reconnects (IP → IMEI)
# ip_imei_cache = {}

# print("🐧 NB-IoT Modem TCP Server (Linux)")
# print("✅ Continuous IMEI Monitoring")
# print("✅ Reconnect Safe")
# print("🚀 Ready")

# # ================= DEVICE DB =================
# def load_devices():
#     try:
#         with open(DEVICE_FILE, "r") as f:
#             return json.load(f)
#     except:
#         return {}

# def save_devices(devices):
#     with open(DEVICE_FILE, "w") as f:
#         json.dump(devices, f, indent=2)

# devices = load_devices()

# # ================= LOGGER =================
# def log_json(protocol, addr, imei, raw_bytes):
#     record = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "protocol": protocol,
#         "ip": addr[0],
#         "port": addr[1],
#         "imei": imei,
#         "data_text": raw_bytes.decode(errors="ignore"),
#         "data_hex": raw_bytes.hex()
#     }

#     print(record)

#     with file_lock:
#         with open(DATA_FILE, "a", encoding="utf-8") as f:
#             f.write(json.dumps(record) + "\n")

# # ================= TCP KEEPALIVE =================
# def enable_keepalive(sock):
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

# # ================= IMEI PARSER =================
# def extract_imei(msg):
#     if msg.startswith("IMEI:"):
#         return msg.replace("IMEI:", "").strip()

#     for part in msg.split(","):
#         if part.isdigit() and len(part) == 15:
#             return part
#     return None

# # ================= TCP HANDLER =================
# def handle_tcp(conn, addr):
#     print(f"🔗 TCP connected: {addr}")

#     enable_keepalive(conn)
#     conn.settimeout(300)  # NB-IoT sleep allowed

#     imei = None

#     try:
#         while True:
#             try:
#                 data = conn.recv(BUFFER_SIZE)

#                 if not data:
#                     print(f"🔌 Modem disconnected normally: {addr}")
#                     break

#                 msg = data.decode(errors="ignore")
#                 detected_imei = extract_imei(msg)

#                 # ----- IMEI DETECTION / CACHE -----
#                 if detected_imei:
#                     imei = detected_imei
#                     ip_imei_cache[addr[0]] = imei

#                 elif addr[0] in ip_imei_cache:
#                     imei = ip_imei_cache[addr[0]]

#                 # ----- VALIDATION -----
#                 if not imei or imei not in devices or not devices[imei]["activated"]:
#                     continue

#                 # ================= SAFE ADDITION =================
#                 # Update last_seen on EVERY valid packet
#                 with device_lock:
#                     devices[imei]["last_seen"] = datetime.now().isoformat()
#                     save_devices(devices)
#                 # =================================================

#                 # ----- LOG DATA -----
#                 log_json("TCP", addr, imei, data)

#             except socket.timeout:
#                 # Normal NB-IoT sleep
#                 continue

#     except Exception as e:
#         print(f"⚠ TCP error {addr}: {e}")

#     finally:
#         conn.close()
#         print(f"❌ TCP session closed: {addr}")

# # ================= TCP SERVER =================
# def tcp_server():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((HOST, PORT))
#     sock.listen(200)

#     print(f"🚀 TCP listening on {HOST}:{PORT}")

#     while True:
#         conn, addr = sock.accept()
#         threading.Thread(
#             target=handle_tcp,
#             args=(conn, addr),
#             daemon=True
#         ).start()

# # ================= MAIN =================
# if __name__ == "__main__":
#     tcp_server()


# import socket
# import threading
# import json
# from datetime import datetime

# # ================= CONFIG =================
# HOST = "0.0.0.0"
# PORT = 5003
# BUFFER_SIZE = 4096

# DATA_FILE = "modem_data.jsonl"
# DEVICE_FILE = "devices.json"

# file_lock = threading.Lock()
# device_lock = threading.Lock()

# # Cache for reconnects (IP → IMEI)
# ip_imei_cache = {}

# print("🐧 NB-IoT Modem TCP Server (Linux)")
# print("✅ Continuous IMEI Monitoring")
# print("✅ Reconnect Safe")
# print("🚀 Ready")

# # ================= DEVICE DB =================
# def load_devices():
#     try:
#         with open(DEVICE_FILE, "r") as f:
#             return json.load(f)
#     except:
#         return {}

# def save_devices(devices):
#     with open(DEVICE_FILE, "w") as f:
#         json.dump(devices, f, indent=2)

# devices = load_devices()

# # ================= LOGGER =================
# def log_json(protocol, addr, imei, raw_bytes):
#     record = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "protocol": protocol,
#         "ip": addr[0],
#         "port": addr[1],
#         "imei": imei,
#         "data_text": raw_bytes.decode(errors="ignore"),
#         "data_hex": raw_bytes.hex()
#     }

#     print(record)

#     with file_lock:
#         with open(DATA_FILE, "a", encoding="utf-8") as f:
#             f.write(json.dumps(record) + "\n")

# # ================= TCP KEEPALIVE =================
# def enable_keepalive(sock):
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

# # ================= IMEI PARSER =================
# def extract_imei(msg):
#     if msg.startswith("IMEI:"):
#         return msg.replace("IMEI:", "").strip()

#     for part in msg.split(","):
#         if part.isdigit() and len(part) == 15:
#             return part
#     return None

# # ================= TCP HANDLER =================
# def handle_tcp(conn, addr):
#     print(f"🔗 TCP connected: {addr}")

#     enable_keepalive(conn)
#     conn.settimeout(300)  # NB-IoT sleep allowed

#     imei = None

#     try:
#         while True:
#             try:
#                 data = conn.recv(BUFFER_SIZE)

#                 if not data:
#                     print(f"🔌 Modem disconnected normally: {addr}")
#                     break

#                 msg = data.decode(errors="ignore")
#                 detected_imei = extract_imei(msg)

#                 # ----- IMEI DETECTION / CACHE -----
#                 if detected_imei:
#                     imei = detected_imei
#                     ip_imei_cache[addr[0]] = imei

#                 elif addr[0] in ip_imei_cache:
#                     imei = ip_imei_cache[addr[0]]

#                 # ----- VALIDATION -----
#                 if not imei or imei not in devices or not devices[imei]["activated"]:
#                     continue

#                 # ================= SAFE ADDITION =================
#                 # Update last_seen on EVERY valid packet
#                 with device_lock:
#                     devices[imei]["last_seen"] = datetime.now().isoformat()
#                     save_devices(devices)
#                 # =================================================

#                 # ----- LOG DATA -----
#                 log_json("TCP", addr, imei, data)

#             except socket.timeout:
#                 # Normal NB-IoT sleep
#                 continue

#     except Exception as e:
#         print(f"⚠ TCP error {addr}: {e}")

#     finally:
#         conn.close()
#         print(f"❌ TCP session closed: {addr}")

# # ================= TCP SERVER =================
# def tcp_server():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((HOST, PORT))
#     sock.listen(200)

#     print(f"🚀 TCP listening on {HOST}:{PORT}")

#     while True:
#         conn, addr = sock.accept()
#         threading.Thread(
#             target=handle_tcp,
#             args=(conn, addr),
#             daemon=True
#         ).start()

# # ================= MAIN =================
# if __name__ == "__main__":
#     tcp_server()

# import socket
# import threading
# import json
# from datetime import datetime

# # ================= CONFIG =================
# HOST = "0.0.0.0"
# PORT = 5003
# BUFFER_SIZE = 4096

# DATA_FILE = "modem_data.jsonl"

# file_lock = threading.Lock()

# # Cache for reconnects (IP → IMEI)
# ip_imei_cache = {}

# print("🐧 NB-IoT Modem TCP Server (Linux)")
# print("✅ Any Modem Accepted")
# print("✅ No Device Registration")
# print("✅ Reconnect Safe")
# print("🚀 Ready")

# # ================= LOGGER =================
# def log_json(protocol, addr, imei, raw_bytes):
#     record = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "protocol": protocol,
#         "ip": addr[0],
#         "port": addr[1],
#         "imei": imei,
#         "data_text": raw_bytes.decode(errors="ignore"),
#         "data_hex": raw_bytes.hex()
#     }

#     print(record)

#     with file_lock:
#         with open(DATA_FILE, "a", encoding="utf-8") as f:
#             f.write(json.dumps(record) + "\n")

# # ================= TCP KEEPALIVE =================
# def enable_keepalive(sock):
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
#     sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

# # ================= IMEI PARSER =================
# def extract_imei(msg):
#     if msg.startswith("IMEI:"):
#         return msg.replace("IMEI:", "").strip()

#     for part in msg.replace("\n", ",").split(","):
#         if part.isdigit() and len(part) == 15:
#             return part

#     return None

# # ================= TCP HANDLER =================
# def handle_tcp(conn, addr):
#     print(f"🔗 TCP connected: {addr}")

#     enable_keepalive(conn)
#     conn.settimeout(300)  # NB-IoT sleep allowed

#     imei = None

#     try:
#         while True:
#             try:
#                 data = conn.recv(BUFFER_SIZE)

#                 if not data:
#                     print(f"🔌 Modem disconnected: {addr}")
#                     break

#                 msg = data.decode(errors="ignore")
#                 detected_imei = extract_imei(msg)

#                 # ----- IMEI CACHE -----
#                 if detected_imei:
#                     imei = detected_imei
#                     ip_imei_cache[addr[0]] = imei
#                     print(f"📟 IMEI detected: {imei}")

#                 elif addr[0] in ip_imei_cache:
#                     imei = ip_imei_cache[addr[0]]

#                 # ----- LOG EVERYTHING -----
#                 log_json("TCP", addr, imei, data)

#             except socket.timeout:
#                 # Normal NB-IoT sleep
#                 continue

#     except Exception as e:
#         print(f"⚠ TCP error {addr}: {e}")

#     finally:
#         conn.close()
#         print(f"❌ TCP session closed: {addr}")

# # ================= TCP SERVER =================
# def tcp_server():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((HOST, PORT))
#     sock.listen(200)

#     print(f"🚀 TCP listening on {HOST}:{PORT}")

#     while True:
#         conn, addr = sock.accept()
#         threading.Thread(
#             target=handle_tcp,
#             args=(conn, addr),
#             daemon=True
#         ).start()

# # ================= MAIN =================
# if __name__ == "__main__":
#     tcp_server()


import socket
import threading
import json
from datetime import datetime
import os

# ================= CONFIG =================
HOST = "0.0.0.0"
PORT = 5003
BUFFER_SIZE = 4096

DATA_FILE = "modem_data.jsonl"
DEVICE_FILE = "devices.json"

file_lock = threading.Lock()
device_lock = threading.Lock()

# Cache for reconnects (IP → IMEI)
ip_imei_cache = {}

print("🐧 NB-IoT Modem TCP Server (Linux)")
print("🔐 Device verification enabled")
print("🚀 Ready")

# ================= LOAD DEVICES =================
def load_devices():
    if not os.path.exists(DEVICE_FILE):
        return {}
    with device_lock, open(DEVICE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_devices(devices):
    with device_lock, open(DEVICE_FILE, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=2)

# ================= LOGGER =================
def log_json(protocol, addr, imei, raw_bytes):
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "protocol": protocol,
        "ip": addr[0],
        "port": addr[1],
        "imei": imei,
        "data_text": raw_bytes.decode(errors="ignore"),
        "data_hex": raw_bytes.hex()
    }

    print(record)

    with file_lock:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

# ================= TCP KEEPALIVE =================
def enable_keepalive(sock):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

# ================= IMEI PARSER =================
def extract_imei(msg):
    if msg.startswith("IMEI:"):
        return msg.replace("IMEI:", "").strip()

    for part in msg.replace("\n", ",").split(","):
        if part.isdigit() and len(part) == 15:
            return part

    return None

# ================= TCP HANDLER =================
def handle_tcp(conn, addr):
    print(f"🔗 TCP connected: {addr}")

    enable_keepalive(conn)
    conn.settimeout(300)

    imei = None
    imei_verified = False

    try:
        while True:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print(f"🔌 Modem disconnected: {addr}")
                    break

                msg = data.decode(errors="ignore")
                detected_imei = extract_imei(msg)

                devices = load_devices()
                now = datetime.now().isoformat()

                # ----- IMEI VERIFICATION -----
                if detected_imei:
                    device = devices.get(detected_imei)

                    if device and device.get("activated") is True:
                        imei = detected_imei
                        imei_verified = True
                        ip_imei_cache[addr[0]] = imei

                        if not device.get("first_seen"):
                            device["first_seen"] = now
                        device["last_seen"] = now
                        devices[imei] = device
                        save_devices(devices)

                        print(f"✅ IMEI verified: {imei}")
                    else:
                        print(f"⛔ IMEI not registered / not activated: {detected_imei}")
                        continue  # ❌ DO NOT LOG DATA

                elif addr[0] in ip_imei_cache:
                    cached = ip_imei_cache[addr[0]]
                    device = devices.get(cached)

                    if device and device.get("activated"):
                        imei = cached
                        imei_verified = True
                        device["last_seen"] = now
                        devices[imei] = device
                        save_devices(devices)

                # ----- LOG DATA ONLY IF VERIFIED -----
                if imei_verified:
                    log_json("TCP", addr, imei, data)
                else:
                    print(f"🚫 Data ignored (IMEI not verified) from {addr}")

            except socket.timeout:
                continue

    except Exception as e:
        print(f"⚠ TCP error {addr}: {e}")

    finally:
        conn.close()
        print(f"❌ TCP session closed: {addr}")

# ================= TCP SERVER =================
def tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(200)

    print(f"🚀 TCP listening on {HOST}:{PORT}")

    while True:
        conn, addr = sock.accept()
        threading.Thread(
            target=handle_tcp,
            args=(conn, addr),
            daemon=True
        ).start()

# ================= MAIN =================
if __name__ == "__main__":
    tcp_server()
