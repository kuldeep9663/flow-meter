import os
import json
import struct
import time
import threading
from flask import Flask, render_template_string

# =====================================================
# CONFIGURATION
# =====================================================
RAW_JSONL = r"d:\Flow-Meter-Server\modem_data.jsonl"
MAX_CACHE = 50
POLL_INTERVAL = 0.5

# =====================================================
# FLASK APP
# =====================================================
app = Flask(__name__)
decoded_cache = []
lock = threading.Lock()

# =====================================================
# REGISTER MAP (PDF VERIFIED – VARIABLES 0–52)
# =====================================================
REGISTER_MAP = [
    ("instantaneous_flow_m3_h", 4, ">f", 1),
    ("pos_flow_int",            4, ">I", 1),
    ("pos_flow_dec",            4, ">I", 0.001),
    ("neg_flow_int",            4, ">I", 1),
    ("neg_flow_dec",            4, ">I", 0.001),
    ("cumulative_flow_m3",      4, ">f", 1),
    ("pipe_diameter",           2, ">H", 1),
    ("sampling_value",          2, ">h", 1),

    ("zero_point_sample",       2, ">h", 1),
    ("instrument_table_no",     2, ">H", 1),
    ("department_no",           2, ">H", 1),
    ("sensor_coefficient",      2, ">H", 1),
    ("atc_sample",              2, ">H", 1),
    ("alarm_info",              2, ">H", 1),
    ("pressure_mpa",            4, ">I", 0.001),
    ("backwater_degree",        2, ">H", 1),
    ("instant_heat",            4, ">f", 1),
    ("accumulated_calories",    4, ">I", 1),
    ("heat_decimal_places",     2, ">H", 1),

    ("cold_total_int",          4, ">I", 1),
    ("cold_total_dec",          4, ">I", 0.001),
    ("instant_heat_unit",       2, ">H", 1),
    ("cumulative_heat_unit",    2, ">H", 1),
    ("hot_department_no",       2, ">H", 1),

    ("pressure_record_1",       2, ">H", 1),
    ("pressure_record_2",       2, ">H", 1),
    ("pressure_record_3",       2, ">H", 1),
    ("pressure_record_4",       2, ">H", 1),
    ("pressure_record_5",       2, ">H", 1),
    ("pressure_record_6",       2, ">H", 1),

    ("flow_volume_1",           4, ">f", 1),
    ("flow_volume_2",           4, ">f", 1),
    ("flow_volume_3",           4, ">f", 1),
    ("flow_volume_4",           4, ">f", 1),
    ("flow_volume_5",           4, ">f", 1),
    ("flow_volume_6",           4, ">f", 1),
]

# =====================================================
# REGISTER DECODER
# =====================================================
def decode_registers(payload: bytes) -> dict:
    decoded = {}
    offset = 0

    for name, size, fmt, scale in REGISTER_MAP:
        chunk = payload[offset:offset + size]
        if len(chunk) < size:
            break

        value = struct.unpack(fmt, chunk)[0]
        decoded[name] = round(value * scale, 3)
        offset += size

    decoded["positive_cumulative_flow_m3"] = (
        decoded.get("pos_flow_int", 0) +
        decoded.get("pos_flow_dec", 0)
    )
    decoded["negative_cumulative_flow_m3"] = (
        decoded.get("neg_flow_int", 0) +
        decoded.get("neg_flow_dec", 0)
    )

    return decoded

# =====================================================
# JSONL FILE WATCHER (FIXED)
# =====================================================
def watch_jsonl():
    print("👀 Watching decoded_output1.jsonl")
    file_pos = 0

    while True:
        try:
            if not os.path.exists(RAW_JSONL):
                time.sleep(1)
                continue

            with open(RAW_JSONL, "r", encoding="utf-8") as f:
                if file_pos > os.path.getsize(RAW_JSONL):
                    file_pos = 0

                f.seek(file_pos)

                while True:
                    line = f.readline()
                    if not line:
                        break

                    file_pos = f.tell()

                    try:
                        rec = json.loads(line)
                    except:
                        continue

                    if "data_hex" not in rec:
                        continue

                    payload = bytes.fromhex(rec["data_hex"])
                    decoded = decode_registers(payload)

                    record = {
                        "upload_time": rec.get("timestamp"),
                        "equipment_number": rec.get("imei"),
                        "decoded": decoded
                    }

                    with lock:
                        decoded_cache.append(record)
                        decoded_cache[:] = decoded_cache[-MAX_CACHE:]

                    print("✅ Decoded:", record["equipment_number"])

        except Exception as e:
            print("⚠ Watcher error:", e)

        time.sleep(POLL_INTERVAL)

# =====================================================
# DASHBOARD
# =====================================================
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>NB-IoT Flow Meter Dashboard</title>
<meta http-equiv="refresh" content="2">
<style>
body { background:#0f172a; color:#e5e7eb; font-family:Arial; }
h1 { color:#38bdf8; text-align:center; }
table { width:100%; border-collapse:collapse; }
th, td { padding:8px; border-bottom:1px solid #334155; text-align:center; }
th { background:#1e293b; position:sticky; top:0; }
</style>
</head>
<body>

<h1>📊 NB-IoT Flow Meter Live Monitoring</h1>

{% if data %}
<table>
<tr>
  <th>Time</th>
  <th>IMEI</th>
  <th>Inst Flow</th>
  <th>Total Flow</th>
  <th>+ Flow</th>
  <th>- Flow</th>
  <th>Pressure (MPa)</th>
</tr>

{% for row in data %}
<tr>
  <td>{{ row.upload_time }}</td>
  <td>{{ row.equipment_number }}</td>
  <td>{{ row.decoded.instantaneous_flow_m3_h }}</td>
  <td>{{ row.decoded.cumulative_flow_m3 }}</td>
  <td>{{ row.decoded.positive_cumulative_flow_m3 }}</td>
  <td>{{ row.decoded.negative_cumulative_flow_m3 }}</td>
  <td>{{ row.decoded.pressure_mpa }}</td>
</tr>
{% endfor %}
</table>
{% else %}
<p style="text-align:center;">Waiting for device data…</p>
{% endif %}

</body>
</html>
"""

@app.route("/")
def index():
    with lock:
        return render_template_string(HTML, data=list(decoded_cache))

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    print("🚀 NB-IoT Flow Meter Decoder Started")
    print("🌐 Dashboard → http://127.0.0.1:5000")

    threading.Thread(target=watch_jsonl, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
