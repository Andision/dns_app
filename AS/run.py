import socket
import json

DNS_RECORDS_FILE = 'dns_records.json'
SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 53533

def load_dns_records():
    try:
        with open(DNS_RECORDS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_dns_record(name, value):
    records = load_dns_records()
    records[name] = value
    with open(DNS_RECORDS_FILE, 'w') as file:
        json.dump(records, file)

def handle_registration(data):
    parts = data.split('\n')
    record_type = parts[0].split('=')[1]
    name = parts[1].split('=')[1]
    value = parts[2].split('=')[1]  # Assuming the IP is sent as part of the registration
    if record_type == 'A':
        save_dns_record(name, value)
        return f"Registered {name} to {value}"
    return "Invalid registration"

def handle_query(data):
    parts = data.split('\n')
    name = parts[1].split('=')[1]
    records = load_dns_records()
    if name in records:
        return f"TYPE=A\nNAME={name}\nVALUE={records[name]}\nTTL=10"
    return "Record not found"

def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_ADDRESS, SERVER_PORT))
    # print(f"Server listening on {SERVER_ADDRESS}:{SERVER_PORT}")
    
    while True:
        data, address = sock.recvfrom(1024)
        data = data.decode('utf-8')
        # print(f"Received from {address}: {data}")
        
        if data.startswith('TYPE=A') and 'NAME=' in data and 'VALUE=' in data:
            response = handle_registration(data)
        elif data.startswith('TYPE=A') and 'NAME=' in data:
            response = handle_query(data)
        else:
            response = "Invalid request"
        
        sock.sendto(response.encode('utf-8'), address)

if __name__ == '__main__':
    print("UDP Server")
    run_server()
