from mysql.connector import pooling
from mysql.connector.pooling import PooledMySQLConnection

from pregen.utils.environment import get_envs
from pregen.utils.singleton import singleton


@singleton
class ConnectionFactory:
    def __init__(self):
        self.connection_pool = pooling.MySQLConnectionPool(**get_envs().database)

    def get_connection(self) -> PooledMySQLConnection:
        return self.connection_pool.get_connection()
