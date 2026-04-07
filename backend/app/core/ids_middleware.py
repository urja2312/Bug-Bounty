"""
Simulated Intrusion Detection System (IDS) / Web Application Firewall
"""
import re
import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Global in-memory list to store WAF alerts for the Streamlit SOC Dashboard
# In a real system, this would write to a specialized database or SIEM.
SECURITY_ALERTS = []

# Regex patterns matching common malicious payloads (OWASP Top 10)
SQL_INJECTION_PATTERN = re.compile(r"(?i)(\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|ALTER)\b)|(--)|(' OR 1=1)|(' OR '1'='1)")
XSS_PATTERN = re.compile(r"(?i)(<\s*script>)|(javascript:)|(onerror\s*=)|(onload\s*=)")
DIRECTORY_TRAVERSAL = re.compile(r"(\.\./)|(\.\.\\)")

class IDSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Check URL Path
        path = str(request.url.path)
        if self.detect_attack(path, "URL Path", request):
            return self.block_request()

        # 2. Check Query String
        query = str(request.url.query)
        if self.detect_attack(query, "URL Query String", request):
            return self.block_request()

        # 3. Check JSON Body (if any)
        # We need to read the body without consuming it permanently for the actual route
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # We can't await request.body() directly here without freezing the route later,
                # but simulated payloads are usually sent as strings. 
                # (Reading the stream in FastAPI middleware is complex, so we rely on path/query 
                #  or parse simple byte strings if available on the wire for the simulation).
                pass
            except Exception:
                pass

        # If clean, process the request normally
        response = await call_next(request)
        return response

    def detect_attack(self, payload: str, source: str, request: Request) -> bool:
        """
        Scans the payload against signature databases.
        Returns True if an attack is detected.
        """
        decoded_payload = requests.utils.unquote(payload) if "%" in payload else payload # Basic decode
        
        attack_type = None
        if SQL_INJECTION_PATTERN.search(decoded_payload):
            attack_type = "SQL Injection (SQLi)"
        elif XSS_PATTERN.search(decoded_payload):
            attack_type = "Cross-Site Scripting (XSS)"
        elif DIRECTORY_TRAVERSAL.search(decoded_payload):
            attack_type = "Directory Traversal"
            
        if attack_type:
            # Generate simulated SOC Alert
            alert = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "ip_address": request.client.host if request.client else "127.0.0.1",
                "attack_type": attack_type,
                "payload_source": source,
                "matched_payload": payload,
                "target_url": str(request.url)
            }
            SECURITY_ALERTS.insert(0, alert)  # Add to top of in-memory log
            print(f"🚨 [IDS WAF] Blocked {attack_type} from {alert['ip_address']} targeting {alert['target_url']}")
            return True
            
        return False

    def block_request(self) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Blocked by Web Application Firewall (WAF)",
                "error": "Malicious payload signature detected. This incident has been logged."
            }
        )
