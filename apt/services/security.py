from flask import Flask, request, abort
import apt.services.config as CONFIG

#
# Verify required security constraints
#
def verify(request):
    verify_api_key(request)
    verify_remote_addr(request)

#
# Verify API Key header parameter
#
def verify_api_key(request):
    if CONFIG.SECURITY_APY_KEY:
        apiKey = request.headers.get("X-API-Key")
        if apiKey != CONFIG.SECURITY_APY_KEY:
            print(f"Unauthorized API Key {apiKey}", flush=True)
            abort(403)

#
# Verify authorized IP
#
def verify_remote_addr(request):
    if CONFIG.SECURITY_AUTHORIZED_IP:
        remoteAddr = request.headers.get("X-Real-IP")
        if remoteAddr != CONFIG.SECURITY_AUTHORIZED_IP:
            print(f"Unauthorized remote IP address {remoteAddr}", flush=True)
            abort(403)