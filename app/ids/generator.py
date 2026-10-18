from snowflake import SnowflakeGenerator

from app.settings import settings


class IdGenerator:
    def __init__(self, node_id: int) -> None:
        self._ids = SnowflakeGenerator(node_id)

    def generate(self) -> int:
        payment_id = next(self._ids)
        if payment_id is None:
            raise RuntimeError("snowflake id was not generated")
        return payment_id


id_generator = IdGenerator(settings.id_generator.node_id)
