import subprocess
import time
import re
import sys
import os

def start_tunnel():
    print("Tunnel ulanmoqda...")
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-R", "80:localhost:8080",
        "nokey@localhost.run"
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="ignore"
        )
        for line in iter(proc.stdout.readline, ''):
            print(line.strip())
            match = re.search(r'(https://[a-zA-Z0-9\-_\.]+\.lhr\.life)', line.strip())
            if match:
                public_url = match.group(1)
                print("\n" + "="*50)
                print(f"PUBLIC_URL={public_url}")
                print("="*50 + "\n")
                with open("tunnel_url.txt", "w") as f:
                    f.write(public_url)
                sys.stdout.flush()
                break
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Tunnel xatoligi: {e}")

if __name__ == "__main__":
    start_tunnel()
