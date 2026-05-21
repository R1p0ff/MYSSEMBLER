from time import sleep
import serial

def programmer(port, hex_bytes, log_interface):
    try:
        serial_com = serial.Serial(port, 115200, timeout=1)
        serial_com.write(bytes([0xFF]))
        sleep(0.2)
        for hex_row in hex_bytes:
            hex_row = "".join(hex_row)
            bytes_package = bytes.fromhex(hex_row)

            package = bytes([0xAA, 0xAA]) + bytes_package + bytes([0xAA])
            serial_com.write(package)
            sleep(0.02)
        serial_com.close()
        log_interface(f"DONE: bytes loaded to ROM", color="#2cde85")
    except:
        try:
            log_interface(f"WARNING: Failed to load byte packet ({bytes_package}) to port {port}", color = "#ff0000")
        except:
            bytes_package = "NO BYTE PACKAGE DETECTED"
            log_interface(f"WARNING: Failed to load byte packet ({bytes_package}) to port {port}", color = "#ff0000")
