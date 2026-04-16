@app.route("/dns-test")
def dns_test():
    hostname = os.environ.get("OBSIDIAN_IP", "").replace("https://", "")
    try:
        result = socket.getaddrinfo(hostname, 443)
        return f"DNS OK: {result[0][4][0]}"
    except Exception as e:
        return f"DNS FAILED: {e}", 500