import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from app.conf.app_config import DBConfig, app_config


class MySQLClientManager:
    def __init__(self, config: DBConfig):
        self.engine: AsyncEngine | None = None
        self.config = config
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def _get_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init(self):
        self.engine = create_async_engine(self._get_url(), pool_size=10, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, autoflush=True, expire_on_commit=False)

    async def close(self):
        if self.engine is None:
            return
        await self.engine.dispose()


meta_mysql_client_manager = MySQLClientManager(app_config.db_meta)
dw_mysql_client_manager = MySQLClientManager(app_config.db_dw)

if __name__ == '__main__':
    dw_mysql_client_manager.init()
    engine = dw_mysql_client_manager.engine


    async def test():
        if engine is None:
            raise RuntimeError("MySQL engine is not initialized")
        if dw_mysql_client_manager.session_factory is None:
            raise RuntimeError("MySQL session factory is not initialized")

        try:
            async with dw_mysql_client_manager.session_factory() as session:
                sql = "select * from fact_order limit 10"
                result = await session.execute(text(sql))
                rows = result.mappings().fetchall()
                print(type(rows))
                print(type(rows[0]))
                print(rows[0]['order_id'])
        finally:
            await dw_mysql_client_manager.close()


    asyncio.run(test())
