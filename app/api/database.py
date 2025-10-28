from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings

# Get database URL from settings
DATABASE_URL = settings.database_url

# 同期URLを非同期URLに変換 (postgresql:// -> postgresql+asyncpg://)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# 非同期エンジンの作成
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.sqlalchemy_echo,
    future=True,
)

# 非同期セッションメーカーの作成
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 依存性注入用のセッション取得関数
async def get_db():
    """
    FastAPIの依存性注入で使用するデータベースセッション取得関数

    使用例:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
