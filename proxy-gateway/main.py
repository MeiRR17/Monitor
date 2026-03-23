import asyncio
import logging
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from sqlmodel import SQLModel, Field, Session, create_engine

# ---------------------------------------------------------------------------
# Database Configuration & Models (Using SQLModel for clean, unified models)
# ---------------------------------------------------------------------------
class TelephonyMetric(SQLModel, table=True):
    """Unified model for both database schema and data validation."""
    __tablename__ = "telephony_metrics"
    
    id: int | None = Field(default=None, primary_key=True)
    server_type: str = Field(index=True)
    metric_name: str = Field(index=True)
    value: float

DB_URL = "postgresql://postgres:password@postgres:5432/telephony_db"
# Initialize the database engine without echo to keep logs clean
engine = create_engine(DB_URL, echo=False)

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ProxyGateway")

# ---------------------------------------------------------------------------
# Core Polling Logic
# ---------------------------------------------------------------------------
TARGET_SERVERS = ["uccx", "cucm", "imp", "mp", "cms", "tgw", "sbc", "expressway"]

async def poll_telephony_metrics():
    """
    Asynchronous background task that continuously polls metrics from all servers.
    This replaces complex threading with modern, efficient asyncio.
    """
    logger.info("Starting asynchronous data polling for all Cisco components...")
    
    # Use a persistent asynchronous HTTP client for better performance
    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            for server in TARGET_SERVERS:
                try:
                    url = f"http://mock-server:8001/api/stats/{server}"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        metrics = data.get("metrics", {})
                        
                        # Prepare data models
                        records = [
                            TelephonyMetric(server_type=server, metric_name="active_calls", value=metrics["active_calls"]["value"]),
                            TelephonyMetric(server_type=server, metric_name="cpu_usage", value=metrics["cpu_usage_percent"]["value"]),
                            TelephonyMetric(server_type=server, metric_name="memory_usage", value=metrics["memory_usage_percent"]["value"])
                        ]
                        
                        # Save to database
                        with Session(engine) as session:
                            session.add_all(records)
                            session.commit()
                            
                        logger.info(f"Collected data for {server.upper()}")
                    else:
                        logger.warning(f"Failed to fetch data for {server.upper()} - Status: {response.status_code}")
                        
                except httpx.RequestError as e:
                    logger.error(f"Network error while connecting to Mock Server for {server.upper()}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error during polling for {server.upper()}: {e}")
            
            # Wait 10 seconds before starting the next polling cycle for all servers
            await asyncio.sleep(10)

# ---------------------------------------------------------------------------
# FastAPI Application & Lifespan Management
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events cleanly."""
    # Create database tables if they do not exist
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables initialized successfully.")
    
    # Start the background polling task
    polling_task = asyncio.create_task(poll_telephony_metrics())
    
    yield # Application runs here
    
    # Cleanup on shutdown
    polling_task.cancel()
    engine.dispose()
    logger.info("Proxy Gateway shutdown cleanly.")

app = FastAPI(title="Telephony Proxy Gateway", lifespan=lifespan)

@app.get("/health")
async def health_check():
    """API endpoint to verify the gateway is running."""
    return {"status": "Proxy Gateway is active and polling"}
