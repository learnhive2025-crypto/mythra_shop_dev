import socket
import ssl
import sys
import certifi

print(f"Python: {sys.version}")
print(f"OpenSSL: {ssl.OPENSSL_VERSION}")

targets = [
    ("google.com", 443),
    ("cluster0.td8nbsq.mongodb.net", 27017) # SRV seed
]

# Add the shard directly if we know it
shard = "ac-82esawg-shard-00-01.td8nbsq.mongodb.net"
targets.append((shard, 27017))

print("\n--- Connectivity Test ---")
for host, port in targets:
    print(f"\nTarget: {host}:{port}")
    try:
        # 1. TCP Connect
        sock = socket.create_connection((host, port), timeout=5)
        print("✅ TCP Connected")
        
        # 2. SSL Handshake
        context = ssl.create_default_context()
        try:
            ssock = context.wrap_socket(sock, server_hostname=host)
            print(f"✅ SSL Handshake OK (Protocol: {ssock.version()})")
            ssock.close()
        except Exception as e:
            print(f"❌ SSL Handshake Failed: {e}")
            
    except Exception as e:
        print(f"❌ TCP Connection Failed: {e}")
