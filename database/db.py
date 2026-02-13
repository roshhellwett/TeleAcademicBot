import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DATABASE_URL

logger = logging.getLogger("DATABASE")

# Railway Optimization: Connection Pooling
# We use a modest pool size to prevent exhausting Postgres connections
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Auto-reconnect if Railway kills idle connection
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

logger.info("✅ DATABASE: PostgreSQL Connection Pool Initialized")
#@academictelebotbyroshhellwett