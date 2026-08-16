from block_pos import Block
from validator_info import ValidatorInfo
from typing import List
import random
import time

class BlockchainPoS:
    """
    Uproszczony łańcuch bloków dla algorytmu Proof of Stake.
    """
    def __init__(self, validators: List[ValidatorInfo]):
        self.chain: List[Block] = []
        self.validators = validators  # lista walidatorow z ich stawkami
        genesis = Block(index=0, prev_hash="0", validator_name="Genesis")
        genesis.block_hash = genesis.calculate_hash()
        self.chain.append(genesis)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def select_validator(self) -> str:
        """
        Wybiera walidatora proporcjonalnie do posiadanego stake'u.
        """
        total_stake = sum(v.stake for v in self.validators)
        # losowanie z zakresu [0, total_stake]
        rnd = random.uniform(0, total_stake)

        cumulative = 0.0
        for validator in self.validators:
            cumulative += validator.stake
            if rnd <= cumulative:
                return validator.name
        # awaryjnie zwracamy ostatniego jesli cokolwiek poszlo nie tak
        return self.validators[-1].name

    def add_block(self, transactions: List):
        """
        Tworzy nowy blok z przekazanymi transakcjami, wybiera walidatora
        i wylicza skrót (block_hash).
        """
        last_block = self.get_last_block()
        new_index = last_block.index + 1

        # wybor walidatora w oparciu o stake
        chosen_validator = self.select_validator()

        # tworzymy blok
        new_block = Block(
            index=new_index,
            prev_hash=last_block.block_hash,
            validator_name=chosen_validator
        )
        new_block.transactions = transactions

        start_time = time.time()
        # w pos nie kopiemy wystarczy obliczyc hash z uwzglednieniem walidatora
        new_block.block_hash = new_block.calculate_hash()
        end_time = time.time()

        self.chain.append(new_block)
        print(f"[PoS] Block {new_index} created by {chosen_validator}. Hash: {new_block.block_hash}")
        print(f"      Time to confirm block: {(end_time - start_time):.6f} seconds\n")
