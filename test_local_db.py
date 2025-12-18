import socket

def check_local_mongo():
    host = "127.0.0.1"
    port = 27017
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        print("✅ Local MongoDB is RUNNING on port 27017")
        return True
    except ConnectionRefusedError:
        print("❌ Local MongoDB is NOT running. Connection Refused.")
        return False
    except Exception as e:
        print(f"❌ Error checking MongoDB: {e}")
        return False

if __name__ == "__main__":
    check_local_mongo()
