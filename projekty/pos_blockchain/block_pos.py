import time
from typing import List
from transaction import Transaction

class Block:
    """
    Uproszczona klasa bloku w PoS. Nie zawiera mechanizmu 'kopania' (mine_block),
    ponieważ blok jest tworzony przez węzeł wyłoniony w oparciu o stake.
    """
    def __init__(self, index: int, prev_hash: str, validator_name: str):
        self.index = index
        self.prev_hash = prev_hash
        self.timestamp = time.time()
        self.transactions: List[Transaction] = []
        self.validator = validator_name  # kto zatwierdza blok
        self.block_hash = ""

    def calculate_hash(self) -> str:
        """
        Oblicza hash (skrót) na podstawie index, prev_hash, timestamp,
        nazwy walidatora i listy transakcji.
        """
        import hashlib
        block_data = (
            str(self.index)
            + self.prev_hash
            + str(self.timestamp)
            + self.validator
            + "".join([f"{tx.sender}{tx.receiver}{tx.amount}" for tx in self.transactions])
        )
        return hashlib.sha256(block_data.encode("utf-8")).hexdigest()
