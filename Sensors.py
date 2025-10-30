import pigpio # Import the pigpio library
import time
import sys


# --- Configuration for three sensors (physical header pins) ---
SENSORS = [
   {"name": "S1", "phys_rx": 19, "phys_tx": 21},
   {"name": "S2", "phys_rx": 18, "phys_tx": 22},
   {"name": "S3", "phys_rx": 23, "phys_tx": 35},  # replaced physical 27 with 35 as requested
]


# --- Pin Mapping ---
PIN_MAP = {
   # Physical Pin: GPIO Number
   3: 2, 5: 3, 7: 4, 8: 14, 10: 15, 11: 17, 12: 18, 13: 27, 15: 22,
   16: 23, 18: 24, 19: 10, 21: 9, 22: 25, 23: 11, 24: 8, 26: 7, 29: 5,
   31: 6, 32: 12, 33: 13, 35: 19, 36: 16, 37: 26, 38: 20, 40: 21
}
# ...existing code...


BAUD_RATE = 115200
COM_COMMAND = b'\x55'


def resolve_pins():
   for s in SENSORS:
       if s["phys_rx"] not in PIN_MAP or s["phys_tx"] not in PIN_MAP:
           print(f"Error: Physical pin {s['phys_rx']} or {s['phys_tx']} is not in the PIN_MAP for sensor {s['name']}.")
           sys.exit(1)
       s["gpio_rx"] = PIN_MAP[s["phys_rx"]]
       s["gpio_tx"] = PIN_MAP[s["phys_tx"]]


def main():
   resolve_pins()


   print(f"--- Sensor Configuration ---")
   for s in SENSORS:
       print(f"{s['name']}: Physical RX {s['phys_rx']} -> GPIO {s['gpio_rx']}, Physical TX {s['phys_tx']} -> GPIO {s['gpio_tx']}")
   print(f"Baud Rate: {BAUD_RATE}")
   print("----------------------------")
  
   print("\nAttempting to connect to pigpio daemon...")
  
   pi = None
   try:
       pi = pigpio.pi()
       if not pi.connected:
           raise IOError("Could not connect to pigpio daemon. Is it running?")
          
       print("Connected to pigpio daemon successfully.")


       # Setup TX outputs and open RX bit-bang for each sensor
       for s in SENSORS:
           pi.set_mode(s["gpio_tx"], pigpio.OUTPUT)
           pi.bb_serial_read_open(s["gpio_rx"], BAUD_RATE, 8)
           print(f"Opened sensor {s['name']}: RX GPIO {s['gpio_rx']}, TX GPIO {s['gpio_tx']}")


       while True:
           # Send command to each sensor (sequentially)
           for s in SENSORS:
               pi.wave_add_serial(s["gpio_tx"], BAUD_RATE, COM_COMMAND)
               wid = pi.wave_create()
               if wid >= 0:
                   pi.wave_send_once(wid)
                   while pi.wave_tx_busy():
                       time.sleep(0.001)
                   pi.wave_delete(wid)
               else:
                   print(f"Failed to create waveform for {s['name']} on TX GPIO {s['gpio_tx']}")


           # Allow sensors time to respond
           time.sleep(0.100)


           # Read and decode each sensor's response
           for s in SENSORS:
               (count, data) = pi.bb_serial_read(s["gpio_rx"])
               prefix = f"[{s['name']}]"
               if count > 0 and data:
                   header_index = data.find(b'\xff')
                   if header_index != -1:
                       if len(data) >= header_index + 4:
                           header = data[header_index]
                           data_h = data[header_index + 1]
                           data_l = data[header_index + 2]
                           rx_cs = data[header_index + 3]
                           cs = (header + data_h + data_l) & 0xFF
                          
                           if rx_cs == cs:
                               distance = (data_h << 8) + data_l
                               print(f"{prefix} Distance: {distance} mm")
                           else:
                               print(f"{prefix} Checksum error. Got: {rx_cs}, Expected: {cs}. Data: {data.hex()}")
                       else:
                           print(f"{prefix} Incomplete packet: {data.hex()}")
                   else:
                       print(f"{prefix} Invalid data received (no header): {data.hex()}")
               else:
                   print(f"{prefix} No data received from sensor.")


           time.sleep(0.01)


   except (IOError, pigpio.error) as e:
       print(f"Error: {e}")
       print("\nPlease check the following:")
       print("- pigpiod is running (sudo pigpiod)")
       print("- Wiring and physical pin assignments")
       print("- No pin conflicts between sensors")
      
   except KeyboardInterrupt:
       print("\nExiting program (Ctrl+C pressed).")
      
   finally:
       if pi and pi.connected:
           print("\nCleaning up GPIO...")
           for s in SENSORS:
               try:
                   pi.bb_serial_read_close(s["gpio_rx"])
               except Exception:
                   pass
           pi.stop()
           print("GPIO cleanup complete. Ports closed.")
          
if __name__ == "__main__":
   main()
