import hashlib
import time
import multiprocessing
from typing import List
from transaction import Transaction


# funkcja wieloprocesowa
def worker(
    start_nonce: int,
    step: int,
    block: "Block",
    target_prefix: str,
    found_nonce: multiprocessing.Value,
    total_attempts: multiprocessing.Value,
    stop_flag: multiprocessing.Value
):
    nonce = start_nonce
    local_attempts = 0
    check_interval = 1000  # ustawiamy stop_flag co 1000 iteracji

    while True:
        if local_attempts % check_interval == 0:
            with stop_flag.get_lock():
                if stop_flag.value == 1:
                    with total_attempts.get_lock():
                        total_attempts.value += local_attempts
                    break

        block.nonce = nonce
        block_hash = block.calculate_hash()
        local_attempts += 1

        if block_hash.startswith(target_prefix):
            with found_nonce.get_lock():
                if found_nonce.value == -1:  # pierwszy proces znajdujacy hash
                    found_nonce.value = nonce
                    with stop_flag.get_lock():
                        stop_flag.value = 1
            with total_attempts.get_lock():
                total_attempts.value += local_attempts
            break

        nonce += step


# klasa Block
class Block:
    def __init__(
        self,
        index: int,
        difficulty: int,
        prev_hash: str = "",
        use_multiprocessing: bool = False
    ):
        self.index = index
        self.prev_hash = prev_hash
        self.timestamp = time.time()
        self.transactions: List[Transaction] = []
        self.nonce = 0
        self.difficulty = difficulty
        self.block_hash = ""
        self.use_multiprocessing = use_multiprocessing
        self.attempts = 0

    def calculate_hash(self) -> str:
        block_data = (
            str(self.index)
            + self.prev_hash
            + str(self.timestamp)
            + str(self.nonce)
            + "".join([f"{tx.sender}{tx.receiver}{tx.amount}" for tx in self.transactions])
        )
        return hashlib.sha256(block_data.encode("utf-8")).hexdigest()

    def mine_block(self):
        # dynamicznie decydujemy czy uzyc wieloprocesowosci
        if self.use_multiprocessing and self.difficulty > 5:
            self._mine_block_multi()
        else:
            self._mine_block_single()

    
    # kopanie jednowatkowe
    def _mine_block_single(self):
        target_prefix = "0" * self.difficulty
        nonce = 0
        attempts = 0

        while True:
            self.nonce = nonce
            block_hash = self.calculate_hash()
            attempts += 1

            if block_hash.startswith(target_prefix):
                self.block_hash = block_hash
                self.attempts = attempts
                print(f"[Block {self.index}] Found valid hash: {self.block_hash}")
                print(f"Attempts (single-thread): {self.attempts}")
                break

            nonce += 1

    
    # kopanie wieloprocesowe
    def _mine_block_multi(self):
        target_prefix = "0" * self.difficulty
        num_workers = min(multiprocessing.cpu_count(), 4)  # Ograniczamy liczbe procesow do 4

        found_nonce = multiprocessing.Value("i", -1)
        total_attempts = multiprocessing.Value("i", 0)
        stop_flag = multiprocessing.Value("i", 0)

        processes = []
        for i in range(num_workers):
            p = multiprocessing.Process(
                target=worker,
                args=(i, num_workers, self, target_prefix, found_nonce, total_attempts, stop_flag)
            )
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        self.nonce = found_nonce.value
        self.block_hash = self.calculate_hash()
        self.attempts = total_attempts.value

        print(f"[Block {self.index}] Found valid hash: {self.block_hash}")
        print(f"Attempts (multi-process): {self.attempts}")