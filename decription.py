# ==========================================================
# EW-02 FLOW METER PROTOCOL DECODER
# Screen + PDF Matched (FINAL • Windows Safe)
# ==========================================================

import os
import json
import struct
from datetime import datetime

# ----------------------------------------------------------
# FILES
# ----------------------------------------------------------
RAW_JSONL = "d:\Flow-Meter-Server\modem_data.jsonl"
OUTPUT_FILE = "decoded_output1.jsonl"

# ----------------------------------------------------------
# REGISTER MAP (FROM PDF + VERIFIED BY DISPLAY)
# ----------------------------------------------------------
REGISTERS = {

    # ---------- FLOW ----------
    0x00: ("flow_m3_h", "float"),          # FLOW
    0x02: ("pos_total_int", "uint"),       # Σ+ integer
    0x04: ("pos_total_dec", "float"),      # Σ+ decimal

    0x06: ("neg_total_int", "uint"),       # Σ− integer
    0x08: ("neg_total_dec", "float"),      # Σ− decimal

    # ---------- VELOCITY ----------
    0x0A: ("velocity_mm_s", "float"),      # Fs

    # ---------- CONFIG ----------
    0x0C: ("pipe_diameter", "uint"),
    0x0E: ("sample_count", "uint"),        # Samp

    # ---------- STATUS ----------
    0x10: ("signal_percent", "uint"),
    0x12: ("alarm_status", "uint"),

    # ---------- PRESSURE / TEMP ----------
    0x14: ("pressure_kpa", "int"),          # Press
    0x16: ("water_temp", "int"),

    # ---------- DEVICE ----------
    0x18: ("mtp", "uint"),                  # MTP
}

# ----------------------------------------------------------
# LOW LEVEL VALUE READERS
# ----------------------------------------------------------
def read_value(data, offset, dtype):
    try:
        if dtype == "float":
            return struct.unpack(">f", data[offset:offset + 4])[0]
        if dtype == "int":
            return struct.unpack(">h", data[offset:offset + 2])[0]
        if dtype == "uint":
            return struct.unpack(">H", data[offset:offset + 2])[0]
    except:
        return None

# ----------------------------------------------------------
# PACKET EXTRACTION
# Format: NBxxx,IMEI,<payload>,END
# ----------------------------------------------------------
def extract_packet_parts(data_hex):
    raw = bytes.fromhex(data_hex)

    p1 = raw.find(b",")
    p2 = raw.find(b",", p1 + 1)

    imei = raw[p1 + 1:p2].decode(errors="ignore")
    payload = raw[p2 + 1:-4]  # remove ",END"

    return imei, payload

# ----------------------------------------------------------
# PAYLOAD DECODER
# ----------------------------------------------------------
def decode_payload(payload):
    decoded = {}

    for addr, (name, dtype) in REGISTERS.items():
        offset = addr * 2
        value = read_value(payload, offset, dtype)

        if isinstance(value, float):
            value = round(value, 6)

        decoded[name] = value

    # ---------- CALCULATED TOTALS ----------
    if decoded["pos_total_int"] is not None and decoded["pos_total_dec"] is not None:
        decoded["total_positive_m3"] = round(
            decoded["pos_total_int"] + decoded["pos_total_dec"], 3
        )

    if decoded["neg_total_int"] is not None and decoded["neg_total_dec"] is not None:
        decoded["total_negative_m3"] = round(
            decoded["neg_total_int"] + decoded["neg_total_dec"], 3
        )

    if decoded.get("total_positive_m3") is not None and decoded.get("total_negative_m3") is not None:
        decoded["net_total_m3"] = round(
            decoded["total_positive_m3"] - decoded["total_negative_m3"], 3
        )

    return decoded

# ----------------------------------------------------------
# MAIN (WINDOWS + LINUX SAFE)
# ----------------------------------------------------------
def main():
    print("🚀 EW-02 Decoder Started")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, RAW_JSONL)
    out_path = os.path.join(base_dir, OUTPUT_FILE)

    with open(raw_path, "r", encoding="utf-8") as src, \
         open(out_path, "w", encoding="utf-8", newline="\n") as out:

        for line in src:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)

            imei, payload = extract_packet_parts(record["data_hex"])
            decoded = decode_payload(payload)

            final_record = {
                "timestamp": record.get("timestamp"),
                "imei": imei,
                "ip": record.get("ip"),
                "port": record.get("port"),
                "decoded": decoded
            }

            out.write(json.dumps(final_record) + "\n")

    print("✅ Decoding complete → decoded_output.jsonl")

# ----------------------------------------------------------
if __name__ == "__main__":
    main()
