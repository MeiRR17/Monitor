import random
from datetime import datetime
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Cisco Telephony Mock Server")

# List of all supported Cisco telephony and infrastructure components
SUPPORTED_SERVERS = [
    "uccx", "cucm", "imp", "mp", "cms", "tgw", "sbc", "expressway"
]

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "Mock Server is healthy"}

@app.get("/api/stats/{server_type}")
async def get_server_stats(server_type: str):
    """
    Generate mock statistics for a specific server type.
    This simulates the real APIs of various Cisco components.
    """
    server_type = server_type.lower()
    if server_type not in SUPPORTED_SERVERS:
        return {"error": "Unsupported server type"}

    # Generate realistic random metrics based on server type
    active_calls = random.randint(10, 1000)
    cpu_usage = random.uniform(10.0, 95.0)
    memory_usage = random.uniform(30.0, 90.0)

    return {
        "server_type": server_type,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "active_calls": {
                "value": active_calls,
                "unit": "count"
            },
            "cpu_usage_percent": {
                "value": round(cpu_usage, 1),
                "unit": "percent"
            },
            "memory_usage_percent": {
                "value": round(memory_usage, 1),
                "unit": "percent"
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
