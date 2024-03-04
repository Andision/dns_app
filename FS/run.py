from flask import Flask, request
import socket
import json

app = Flask(__name__)

# Simple function to calculate Fibonacci number
def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    return fibonacci(n-1) + fibonacci(n-2)

@app.route('/register', methods=['PUT'])
def register():
    # Parse the request body
    data = request.json
    hostname = data.get('hostname')
    ip = data.get('ip')
    as_ip = data.get('as_ip')
    as_port = data.get('as_port')

    # Validate the data
    if not all([hostname, ip, as_ip, as_port]):
        return "Missing required registration information",400
    
    print(hostname, ip, as_ip, as_port)

    # Prepare the DNS registration message
    dns_message = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10\n"

    # Send the registration message to the Authoritative Server via UDP
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(dns_message.encode(), (as_ip, int(as_port)))
            # Assuming AS responds with some acknowledgment
            response, _ = sock.recvfrom(1024)
            print("AS response:", response.decode())
    except Exception as e:
        return "Failed to register with AS", 500

    return "Registration successful", 201

@app.route('/fibonacci', methods=['GET'])
def get_fibonacci():
    number = request.args.get('number', type=int)
    if number is None or number < 0:
        return "Invalid input for Fibonacci calculation", 400

    fib_number = fibonacci(number)
    return str(fib_number), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)
