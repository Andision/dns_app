from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    # Extract query parameters
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')

    # Validate parameters
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad Request: Missing parameters", 400

    # Query the Authoritative Server (AS) for the IP address of the given hostname
    try:
        dns_query = f"TYPE=A\nNAME={hostname}\n"
        # Assuming AS provides a simple UDP interface for queries
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(dns_query.encode(), (as_ip, int(as_port)))
        data, _ = sock.recvfrom(512)  # Buffer size 512 bytes
        response = data.decode().split('\n')
        if response[1].split("=")[1] != hostname or response[0].split("=")[1] != 'A':
            return "Invalid DNS response", 500
        ip_address = response[2].split("=")[1]
    except Exception as e:
        return "Error querying DNS", 500

    # Make a request to the Fibonacci service
    try:
        fib_service_url = f"http://{ip_address}:{fs_port}/fibonacci?number={number}"
        fib_response = requests.get(fib_service_url)
        if fib_response.status_code != 200:
            return "Failed to get Fibonacci number", 500
        fib_number = fib_response.text
    except Exception as e:
        return "Error requesting Fibonacci number", 500

    return jsonify(fibonacci_number=fib_number), 200

app.run(host='0.0.0.0', port=8080, debug=True)