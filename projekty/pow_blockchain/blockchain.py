import time
from block import Block
import json

def save_blockchain_to_file(chain, filename="chain_data.json"):
    data = []
    for block in chain:
        data.append({
            "index": block.index,
            "prev_hash": block.prev_hash,
            "timestamp": block.timestamp,
            "transactions": [
                {"sender": tx.sender, "receiver": tx.receiver, "amount": tx.amount}
                for tx in block.transactions
            ],
            "nonce": block.nonce,
            "block_hash": block.block_hash
        })
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


class Blockchain:
    def __init__(self, difficulty: int):
        self.difficulty = difficulty
        self.chain = []
        # tworzenie bloku genesis
        genesis = Block(index=0, prev_hash="0", difficulty=self.difficulty)
        genesis.block_hash = genesis.calculate_hash()
        self.chain.append(genesis)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, new_block: Block):
      
        new_block.prev_hash = self.get_last_block().block_hash
        new_block.difficulty = self.difficulty

        print(f"[Blockchain] Mining block {new_block.index} with difficulty={self.difficulty}...")
        start_time = time.time()

        new_block.mine_block()

        end_time = time.time()
        self.chain.append(new_block)
        print(f"[Blockchain] Block {new_block.index} mined: {new_block.block_hash}")
        #print(f"             Mining took {end_time - start_time:.4f} seconds\n")