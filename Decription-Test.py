# import struct
# import json

# def decode_payload(payload_bytes):
#     """Decodes the binary segment based on register addresses[cite: 9, 11, 14, 17]."""
#     def get_val(addr_hex, data_type, length):
#         # Every two bytes are defined as a register 
#         start_index = int(addr_hex.replace('H', ''), 16) * 2
#         chunk = payload_bytes[start_index : start_index + length]
        
#         if len(chunk) < length:
#             return None
        
#         try:
#             if data_type == 'float':
#                 return round(struct.unpack('>f', chunk)[0], 4)
#             elif data_type == 'long':
#                 return struct.unpack('>l', chunk)[0]
#             elif data_type == 'int':
#                 return struct.unpack('>h', chunk)[0]
#         except:
#             return None
#         return None

#     return {
#         # Page 1 & 2: Flow Measurements
#         "transient_flow": get_val('00H', 'float', 4),           # [cite: 11]
#         "total_cumulative_flow": get_val('02H', 'long', 4),    # [cite: 11]
#         "total_cumulative_decimal": get_val('04H', 'float', 4),# [cite: 11]
#         "negative_cumulative_flow": get_val('06H', 'long', 4), # [cite: 11]
#         "pressure": get_val('13H', 'int', 2),                  # 
        
#         # Page 2 & 3: Heat/Cold Measurements
#         "instantaneous_heat": get_val('16H', 'float', 4),      # 
#         "cumulative_calories": get_val('18H', 'long', 4),      # 
#         "cumulative_cold_integer": get_val('1CH', 'long', 4),  # [cite: 17]
        
#         # Status Codes
#         "sample_value": get_val('0DH', 'int', 2),              # [cite: 11]
#         "instrument_id": get_val('0FH', 'int', 2)              # 
#     }

# def process_jsonl(input_file, output_file):
#     results = []
    
#     with open(input_file, 'r') as f:
#         for line in f:
#             if not line.strip():
#                 continue
                
#             record = json.loads(line)
#             # Use the data_hex field provided in your JSON
#             hex_str = record.get("data_hex", "")
            
#             if hex_str:
#                 raw_bytes = bytes.fromhex(hex_str)
#                 # Split by comma separator [cite: 8]
#                 segments = raw_bytes.split(b',')
                
#                 if len(segments) >= 3:
#                     # Segment 0: Header/IP, Segment 1: IMEI/ID, Segment 2: Data [cite: 5]
#                     payload = segments[2]
#                     decoded_measurements = decode_payload(payload)
                    
#                     # Merge original metadata with decoded results
#                     output_entry = {
#                         "timestamp": record.get("timestamp"),
#                         "imei": record.get("imei"),
#                         "decoded": decoded_measurements
#                     }
#                     results.append(output_entry)

#     # Save processed data
#     with open(output_file, 'w') as f_out:
#         for entry in results:
#             f_out.write(json.dumps(entry) + '\n')
    
#     print(f"Processing complete. Decoded {len(results)} entries into {output_file}.")

# # Run the processor
# process_jsonl('modem_data.jsonl', 'decoded_output2.jsonl')
# import struct
# import json

# class FlowMeterDecoder:
#     def __init__(self):
#         # Mapping based on PDF Address Codes (Hex)
#         # Format: (Byte_Offset, Data_Type, Name)
#         self.registry = {
#             0x00: ('float', "transient_flow"),            # 00H
#             0x02: ('long',  "total_cumulative_int"),      # 02H
#             0x04: ('float', "total_cumulative_dec"),      # 04H
#             0x06: ('long',  "negative_cumulative_int"),   # 06H
#             0x08: ('float', "negative_cumulative_dec"),   # 08H
#             0x0D: ('int',   "sampling_value"),            # 0DH
#             0x13: ('int',   "pressure"),                  # 13H
#             0x16: ('float', "instantaneous_heat"),        # 16H
#             0x18: ('long',  "cumulative_heat_int"),       # 18H
#             0x1A: ('float', "cumulative_heat_dec"),       # 1AH
#             0x1C: ('long',  "cumulative_cold_int"),       # 1CH
#             0x1E: ('float', "cumulative_cold_dec"),       # 1EH
#         }

#     def decode_line(self, json_line):
#         try:
#             data = json.loads(json_line)
#             hex_payload = data.get("data_hex", "")
#             if not hex_payload:
#                 return None

#             raw_bytes = bytes.fromhex(hex_payload)
            
#             # The protocol separates Header, IMEI, and Data with commas (0x2c)
#             parts = raw_bytes.split(b',')
#             if len(parts) < 3:
#                 return {"error": "Incomplete packet structure"}

#             # The actual meter data segment
#             meter_data = parts[2]
#             results = {
#                 "timestamp": data.get("timestamp"),
#                 "imei": data.get("imei"),
#                 "measurements": {}
#             }

#             for addr, (dtype, name) in self.registry.items():
#                 byte_pos = addr * 2
                
#                 if dtype == 'float':
#                     val = struct.unpack('>f', meter_data[byte_pos:byte_pos+4])[0]
#                     results["measurements"][name] = round(val, 4)
#                 elif dtype == 'long':
#                     val = struct.unpack('>l', meter_data[byte_pos:byte_pos+4])[0]
#                     results["measurements"][name] = val
#                 elif dtype == 'int':
#                     val = struct.unpack('>h', meter_data[byte_pos:byte_pos+2])[0]
#                     results["measurements"][name] = val

#             return results
#         except Exception as e:
#             return {"error": str(e)}

# def process_file(input_path, output_path):
#     decoder = FlowMeterDecoder()
#     with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
#         for line in infile:
#             decoded = decoder.decode_line(line)
#             if decoded:
#                 outfile.write(json.dumps(decoded) + '\n')

# # Usage
# if __name__ == "__main__":
#     process_file('modem_data.jsonl', 'decoded_output2.jsonl')
#     print("Decoding complete. Results saved to proper_decoded_output2.jsonl")

# import struct
# import json
# import time

# class FlowMeterAccurateDecoder:
#     def __init__(self):
#         # Precise Mapping from Protocol Manual
#         # (Hex Address, Data Type, Field Name)
#         self.mapping = [
#             (0x00, 'float', 'instantaneous_flow'),       # 
#             (0x02, 'long',  'pos_cum_flow_int'),         # 
#             (0x04, 'float', 'pos_cum_flow_dec'),         # 
#             (0x06, 'long',  'neg_cum_flow_int'),         # 
#             (0x08, 'float', 'neg_cum_flow_dec'),         # 
#             (0x0D, 'int',   'sampling_value'),           # 
#             (0x13, 'int',   'pressure')                  # 
#         ]

#     def decode_packet(self, data_hex):
#         try:
#             # Protocol structure: Header, Address, DeviceID, DATA, Tail [cite: 5]
#             raw_bytes = bytes.fromhex(data_hex)
#             segments = raw_bytes.split(b',')
            
#             if len(segments) < 3:
#                 return None
            
#             # The 3rd segment is the hex data field 
#             data_field = segments[2]
#             results = {}

#             for addr, dtype, name in self.mapping:
#                 offset = addr * 2 # Every address is 2 bytes 
                
#                 if dtype == 'float': # 4 bytes [cite: 13]
#                     chunk = data_field[offset:offset+4]
#                     if len(chunk) == 4:
#                         results[name] = round(struct.unpack('>f', chunk)[0], 4)
#                 elif dtype == 'long': # 4 bytes [cite: 13]
#                     chunk = data_field[offset:offset+4]
#                     if len(chunk) == 4:
#                         results[name] = struct.unpack('>l', chunk)[0]
#                 elif dtype == 'int': # 2 bytes [cite: 13]
#                     chunk = data_field[offset:offset+2]
#                     if len(chunk) == 2:
#                         results[name] = struct.unpack('>h', chunk)[0]

#             # Combine Integer and Decimal parts for absolute accuracy 
#             if 'pos_cum_flow_int' in results and 'pos_cum_flow_dec' in results:
#                 results['cumulative_flow_positive'] = results['pos_cum_flow_int'] + results['pos_cum_flow_dec']
            
#             if 'neg_cum_flow_int' in results and 'neg_cum_flow_dec' in results:
#                 results['cumulative_flow_negative'] = results['neg_cum_flow_int'] + results['neg_cum_flow_dec']

#             return results
#         except Exception:
#             return None

#     def monitor_file(self, filename):
#         print(f"Reading {filename}...")
#         with open(filename, 'r') as f:
#             while True:
#                 line = f.readline()
#                 if not line:
#                     time.sleep(0.5)
#                     continue
                
#                 record = json.loads(line)
#                 decoded = self.decode_packet(record.get("data_hex", ""))
                
#                 if decoded:
#                     print(f"--- Decoded Data {record.get('timestamp')} ---")
#                     print(f"IMEI: {record.get('imei')}")
#                     print(f"Instantaneous Flow: {decoded.get('instantaneous_flow')} m³/h")
#                     print(f"Positive Cumulative: {decoded.get('cumulative_flow_positive')} m³")
#                     print(f"Negative Cumulative: {decoded.get('cumulative_flow_negative')} m³")
#                     print(f"Pressure: {decoded.get('pressure')} kPa")
#                     print(f"Sampling Value: {decoded.get('sampling_value')}")
#                     print("-" * 40)

# if __name__ == "__main__":
#     decoder = FlowMeterAccurateDecoder()
#     decoder.monitor_file('modem_data.jsonl')

# import struct
# import json
# import time

# class FlowMeterFinalProcessor:
#     def __init__(self):
#         # Precise Mapping from Protocol Manual (Address Code * 2 = Byte Offset)
#         # Format: (Hex Address, Data Type, Field Name)
#         self.definitions = [
#             (0x00, 'float', 'transient_flow'),
#             (0x02, 'long',  'total_cumulative_whole'),
#             (0x04, 'float', 'total_cumulative_decimal'),
#             (0x06, 'long',  'negative_cumulative_whole'),
#             (0x08, 'float', 'negative_cumulative_decimal'),
#             (0x0D, 'int',   'sampling_value'),
#             (0x0E, 'int',   'zero_point_sample'),
#             (0x0F, 'int',   'instrument_number'),
#             (0x13, 'int',   'pressure'),
#             (0x14, 'int',   'water_temperature'),
#             (0x16, 'float', 'instantaneous_heat'),
#             (0x18, 'long',  'cumulative_heat_whole'),
#             (0x1A, 'float', 'cumulative_heat_decimal'),
#             (0x1C, 'long',  'cumulative_cold_whole'),
#             (0x1E, 'float', 'cumulative_cold_decimal'),
#             # Historical Records
#             (0x22, 'int',   'pressure_record_1'),
#             (0x23, 'int',   'pressure_record_2'),
#             (0x24, 'int',   'pressure_record_3'),
#             (0x28, 'float', 'flow_record_1'),
#             (0x2A, 'float', 'flow_record_2'),
#             (0x30, 'float', 'flow_record_5')
#         ]

#     def decode_payload(self, payload_bytes):
#         results = {}
#         for addr, dtype, name in self.definitions:
#             offset = addr * 2  # Address Code to Byte Offset
            
#             try:
#                 if dtype == 'float':
#                     chunk = payload_bytes[offset : offset + 4]
#                     if len(chunk) == 4:
#                         results[name] = round(struct.unpack('>f', chunk)[0], 4)
#                 elif dtype == 'long':
#                     chunk = payload_bytes[offset : offset + 4]
#                     if len(chunk) == 4:
#                         results[name] = struct.unpack('>l', chunk)[0]
#                 elif dtype == 'int':
#                     chunk = payload_bytes[offset : offset + 2]
#                     if len(chunk) == 2:
#                         results[name] = struct.unpack('>h', chunk)[0]
#             except Exception:
#                 results[name] = 0 # Default if data is missing or corrupted
#         return results

#     def process_continuous(self, input_file, output_file):
#         print(f"Starting processing: {input_file} -> {output_file}")
        
#         # Open both files: input for reading, output for appending
#         with open(input_file, 'r') as f_in, open(output_file, 'a') as f_out:
#             while True:
#                 line = f_in.readline()
#                 if not line:
#                     time.sleep(0.5) # Wait for new entries
#                     continue
                
#                 try:
#                     record = json.loads(line)
#                     hex_str = record.get("data_hex", "")
                    
#                     # Convert Hex to bytes and split by comma
#                     raw_bytes = bytes.fromhex(hex_str)
#                     segments = raw_bytes.split(b',')
                    
#                     if len(segments) >= 3:
#                         # Extract the data segment (the 3rd part)
#                         data_segment = segments[2]
#                         measurements = self.decode_payload(data_segment)
                        
#                         # Create the exact JSON format requested
#                         output_record = {
#                             "timestamp": record.get("timestamp"),
#                             "imei": record.get("imei"),
#                             "decoded_measurements": measurements
#                         }
                        
#                         # Write to result file
#                         f_out.write(json.dumps(output_record) + "\n")
#                         f_out.flush() # Ensure it writes to disk immediately
                        
#                         print(f"Logged: {record.get('timestamp')} | IMEI: {record.get('imei')}")
                
#                 except Exception as e:
#                     print(f"Error processing line: {e}")

# if __name__ == "__main__":
#     processor = FlowMeterFinalProcessor()
#     # Replace these filenames with your actual file paths
#     processor.process_continuous('modem_data.jsonl', 'decord_result1.jsonl')

import struct
import json
import time

class FlowMeterAccurateDecoder:
    def __init__(self):
        # Precise Mapping from Protocol Manual (Address Code * 2 = Byte Offset)
        self.mapping = [
            (0x00, 'float', 'transient_flow'),              # Instantaneous flow
            (0x02, 'long',  'total_cumulative_whole'),       # Positive integer part
            (0x04, 'float', 'total_cumulative_decimal'),     # Positive decimal part
            (0x06, 'long',  'negative_cumulative_whole'),    # Negative integer part
            (0x08, 'float', 'negative_cumulative_decimal'),  # Negative decimal part
            (0x0D, 'int',   'sampling_value'),               # Sensor sampling
            (0x0E, 'int',   'zero_point_sample'),            # Zero point calibration
            (0x0F, 'int',   'instrument_number'),            # Device ID
            (0x13, 'int',   'pressure'),                     # Water pressure
            (0x14, 'int',   'water_temperature'),            # Temperature
            (0x16, 'float', 'instantaneous_heat'),           # Heat flow
            (0x18, 'long',  'cumulative_heat_whole'),        # Heat integer
            (0x1A, 'float', 'cumulative_heat_decimal'),      # Heat decimal
            (0x1C, 'long',  'cumulative_cold_whole'),        # Cold integer
            (0x1E, 'float', 'cumulative_cold_decimal'),      # Cold decimal
            (0x22, 'int',   'pressure_record_1'),
            (0x23, 'int',   'pressure_record_2'),
            (0x24, 'int',   'pressure_record_3'),
            (0x28, 'float', 'flow_record_1'),
            (0x2A, 'float', 'flow_record_2'),
            (0x30, 'float', 'flow_record_5')
        ]

    def decode_packet(self, data_hex):
        try:
            # Protocol structure: NB[Header],[IMEI],[DATA],END
            raw_bytes = bytes.fromhex(data_hex)
            segments = raw_bytes.split(b',')
            
            if len(segments) < 3:
                return None
            
            data_field = segments[2]
            results = {}

            for addr, dtype, name in self.mapping:
                offset = addr * 2
                
                if dtype == 'float':
                    chunk = data_field[offset:offset+4]
                    if len(chunk) == 4:
                        results[name] = round(struct.unpack('>f', chunk)[0], 4)
                elif dtype == 'long':
                    chunk = data_field[offset:offset+4]
                    if len(chunk) == 4:
                        results[name] = struct.unpack('>l', chunk)[0]
                elif dtype == 'int':
                    chunk = data_field[offset:offset+2]
                    if len(chunk) == 2:
                        results[name] = struct.unpack('>h', chunk)[0]
                else:
                    results[name] = 0
            return results
        except Exception:
            return None

    def monitor_and_save(self, input_file, output_file):
        print(f"Monitoring {input_file}... Saving to {output_file}")
        
        # Open output file in append mode ('a')
        with open(input_file, 'r') as f_in, open(output_file, 'a') as f_out:
            while True:
                line = f_in.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                try:
                    record = json.loads(line)
                    decoded_measurements = self.decode_packet(record.get("data_hex", ""))
                    
                    if decoded_measurements:
                        # Construct the requested JSON format
                        output_entry = {
                            "timestamp": record.get("timestamp"),
                            "imei": record.get("imei"),
                            "decoded_measurements": decoded_measurements
                        }
                        
                        # Write to JSONL file
                        f_out.write(json.dumps(output_entry) + "\n")
                        f_out.flush() # Ensure data is written immediately
                        
                        print(f"Processed: {record.get('timestamp')} | IMEI: {record.get('imei')}")
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    decoder = FlowMeterAccurateDecoder()
    # Continuous running loop
    decoder.monitor_and_save('modem_data.jsonl', 'decord_result1.jsonl')