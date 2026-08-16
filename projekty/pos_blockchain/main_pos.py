from blockchain_pos import BlockchainPoS
from validator_info import ValidatorInfo
from transaction import Transaction
from block_pos import Block
import matplotlib.pyplot as plt
import random
import time
import psutil
import numpy as np

def measure_resources():
    """Pomiar użycia CPU i RAM."""
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram_usage = psutil.virtual_memory().percent
    return cpu_usage, ram_usage

def scenario_3_and_4_combined(repetitions=20):
    """
    Połączony Scenariusz 3 i 4 z pomiarami zasobów i wielokrotnymi powtórkami.
    """
    total_stake = 100
    validators = [
        ValidatorInfo(name="Dominant", stake=60.0),
        ValidatorInfo(name="Secondary", stake=30.0),
        ValidatorInfo(name="Minor", stake=10.0)
    ]

    all_cpu_usage = []
    all_ram_usage = []
    all_tps = []
    all_total_times = []

    print("=== Połączony Scenariusz 3 i 4: Dominacja walidatora przy 1000 transakcji ===")
    for rep in range(repetitions):
        pos_chain = BlockchainPoS(validators=validators)
        mempool = [Transaction(f"User_{random.randint(1, 100)}", f"User_{random.randint(1, 100)}", 
                              random.uniform(0.1, 10.0)) for _ in range(1000)]

        transactions_per_block = 1000 // 50
        total_time = 0.0
        cpu_usage_list = []
        ram_usage_list = []
        count_chosen = {v.name: 0 for v in validators}

        print(f"\nPowtórka {rep + 1}/{repetitions}")
        for i in range(50):
            block_transactions = mempool[i * transactions_per_block:(i + 1) * transactions_per_block]
            start_time = time.time()
            cpu_before, ram_before = measure_resources()
            pos_chain.add_block(block_transactions)
            cpu_after, ram_after = measure_resources()
            end_time = time.time()
            block_time = end_time - start_time
            total_time += block_time

            cpu_usage_list.append((cpu_before + cpu_after) / 2)
            ram_usage_list.append((ram_before + ram_after) / 2)
            chosen = pos_chain.get_last_block().validator
            count_chosen[chosen] += 1

        avg_cpu = np.mean(cpu_usage_list)
        avg_ram = np.mean(ram_usage_list)
        total_transactions = 1000
        tps = total_transactions / total_time if total_time > 0 else 0

        all_cpu_usage.append(avg_cpu)
        all_ram_usage.append(avg_ram)
        all_tps.append(tps)
        all_total_times.append(total_time)

    # srednie i odchylenia standardowe
    mean_cpu = np.mean(all_cpu_usage)
    std_cpu = np.std(all_cpu_usage)
    mean_ram = np.mean(all_ram_usage)
    std_ram = np.std(all_ram_usage)
    mean_tps = np.mean(all_tps)
    std_tps = np.std(all_tps)
    mean_total_time = np.mean(all_total_times)
    std_total_time = np.std(all_total_times)

    # analiza dominacji walidatora ostatnia proba
    print("\n--- Analiza dominacji walidatora (ostatnia powtórka) ---")
    for validator in validators:
        percentage = (count_chosen[validator.name] / 50) * 100
        print(f"Walidator: {validator.name}, Stake: {validator.stake} ({validator.stake}%), "
              f"Bloki: {count_chosen[validator.name]} ({percentage:.2f}%)")

    plt.bar([v.name for v in validators], [count_chosen[v.name] for v in validators], color='blue')
    plt.xlabel("Walidator")
    plt.ylabel("Liczba wygenerowanych bloków")
    plt.title("Scenariusz 3+4: Wpływ walidatora z ~60% stake (50 bloków)")
    plt.show()

    print("\n--- Analiza przepustowości i zasobów (średnie z 20 powtórek) ---")
    print(f"Średni czas przetwarzania 50 bloków: {mean_total_time:.6f} ± {std_total_time:.6f} sekund")
    print(f"Średnia przepustowość (TPS): {mean_tps:.2f} ± {std_tps:.2f} transakcji na sekundę")
    print(f"Średnie użycie CPU: {mean_cpu:.2f} ± {std_cpu:.2f}%")
    print(f"Średnie użycie RAM: {mean_ram:.2f} ± {std_ram:.2f}%")

    # zapis do txt
    with open("pos_results.txt", "w") as f:
        f.write("=== Wyniki Scenariusza 3 i 4 ===\n")
        for rep in range(repetitions):
            f.write(f"Powtórka {rep + 1}: CPU={all_cpu_usage[rep]:.2f}%, RAM={all_ram_usage[rep]:.2f}%, "
                    f"TPS={all_tps[rep]:.2f}, Czas={all_total_times[rep]:.6f}s\n")
        f.write("\nŚrednie wartości ± Odchylenie standardowe:\n")
        f.write(f"CPU: {mean_cpu:.2f} ± {std_cpu:.2f}%\n")
        f.write(f"RAM: {mean_ram:.2f} ± {std_ram:.2f}%\n")
        f.write(f"TPS: {mean_tps:.2f} ± {std_tps:.2f}\n")
        f.write(f"Czas: {mean_total_time:.6f} ± {std_total_time:.6f}s\n")

    return mean_cpu, std_cpu, mean_ram, std_ram, mean_tps, std_tps, mean_total_time, std_total_time

def scenario_5_nothing_at_stake(repetitions=20):
    """
    Scenariusz 5 z pomiarami zasobów, TPS, czasem i wielokrotnymi powtórkami.
    """
    total_stake = 100
    validators = [
        ValidatorInfo(name="Dominant", stake=60.0),
        ValidatorInfo(name="Secondary", stake=30.0),
        ValidatorInfo(name="Minor", stake=10.0)
    ]

    all_cpu_usage = []
    all_ram_usage = []
    all_total_times = []
    all_tps = []

    print("=== Scenariusz 5: Nothing at Stake ===")
    for rep in range(repetitions):
        pos_chain = BlockchainPoS(validators=validators)
        mempool = [Transaction(f"User_{random.randint(1, 100)}", f"User_{random.randint(1, 100)}", 
                              random.uniform(0.1, 10.0)) for _ in range(1000)]

        transactions_per_block = 1000 // 50
        total_time = 0.0
        cpu_usage_list = []
        ram_usage_list = []
        count_chosen_main = {v.name: 0 for v in validators}

        print(f"\nPowtórka {rep + 1}/{repetitions}: Tworzenie głównego łańcucha")
        for i in range(50):
            block_transactions = mempool[i * transactions_per_block:(i + 1) * transactions_per_block]
            start_time = time.time()
            cpu_before, ram_before = measure_resources()
            pos_chain.add_block(block_transactions)
            cpu_after, ram_after = measure_resources()
            end_time = time.time()
            total_time += end_time - start_time
            cpu_usage_list.append((cpu_before + cpu_after) / 2)
            ram_usage_list.append((ram_before + ram_after) / 2)
            chosen = pos_chain.get_last_block().validator
            count_chosen_main[chosen] += 1

        fork_chain = pos_chain.chain[:40]
        count_chosen_fork = {v.name: 0 for v in validators}

        print(f"Powtórka {rep + 1}/{repetitions}: Atak - tworzenie forka")
        for i in range(10):
            new_index = fork_chain[-1].index + 1
            new_block = Block(new_index, fork_chain[-1].block_hash, "Dominant")
            block_transactions = mempool[(40 + i) * transactions_per_block:(40 + i + 1) * transactions_per_block]
            start_time = time.time()
            cpu_before, ram_before = measure_resources()
            new_block.transactions = block_transactions
            new_block.block_hash = new_block.calculate_hash()
            cpu_after, ram_after = measure_resources()
            end_time = time.time()
            total_time += end_time - start_time
            fork_chain.append(new_block)
            cpu_usage_list.append((cpu_before + cpu_after) / 2)
            ram_usage_list.append((ram_before + ram_after) / 2)
            count_chosen_fork["Dominant"] += 1

        avg_cpu = np.mean(cpu_usage_list)
        avg_ram = np.mean(ram_usage_list)
        total_transactions = 1000  # 1000 transkacji w glownym lancuchu
        tps = total_transactions / total_time if total_time > 0 else 0

        all_cpu_usage.append(avg_cpu)
        all_ram_usage.append(avg_ram)
        all_total_times.append(total_time)
        all_tps.append(tps)

    # srednie i odchylenia standardowe
    mean_cpu = np.mean(all_cpu_usage)
    std_cpu = np.std(all_cpu_usage)
    mean_ram = np.mean(all_ram_usage)
    std_ram = np.std(all_ram_usage)
    mean_total_time = np.mean(all_total_times)
    std_total_time = np.std(all_total_times)
    mean_tps = np.mean(all_tps)
    std_tps = np.std(all_tps)

    # analiza ostatnia proba
    print("\n--- Analiza: Główny łańcuch (bloki 41-50) ---")
    for validator in validators:
        percentage = (count_chosen_main[validator.name] / 50) * 100
        print(f"Walidator: {validator.name}, Stake: {validator.stake} ({validator.stake}%), "
              f"Bloki: {count_chosen_main[validator.name]} ({percentage:.2f}%)")

    print("\n--- Analiza: Fork (bloki 41-50) ---")
    for validator in validators:
        percentage = (count_chosen_fork[validator.name] / 10) * 100
        print(f"Walidator: {validator.name}, Bloki w forku: {count_chosen_fork[validator.name]} ({percentage:.2f}%)")

    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    x = range(len(validators))
    plt.bar(x, [count_chosen_main[v.name] for v in validators], bar_width, label="Główny łańcuch", color='blue')
    plt.bar([i + bar_width for i in x], [count_chosen_fork[v.name] for v in validators], bar_width, label="Fork", color='red')
    plt.xlabel("Walidator")
    plt.ylabel("Liczba wygenerowanych bloków")
    plt.title("Scenariusz 5: Porównanie głównego łańcucha i forka")
    plt.xticks([i + bar_width / 2 for i in x], [v.name for v in validators])
    plt.legend()
    plt.show()

    print("\n--- Wnioski: Problem 'Nothing at Stake' ---")
    print(f"Średni czas przetwarzania (20 powtórek): {mean_total_time:.6f} ± {std_total_time:.6f} sekund")
    print(f"Średnia przepustowość (TPS): {mean_tps:.2f} ± {std_tps:.2f} transakcji na sekundę")
    print(f"Średnie użycie CPU (20 powtórek): {mean_cpu:.2f} ± {std_cpu:.2f}%")
    print(f"Średnie użycie RAM (20 powtórek): {mean_ram:.2f} ± {std_ram:.2f}%")
    print("Brak slashingu pozwala 'Dominant' na tworzenie forka bez konsekwencji.")

    # zapis do txt
    with open("pos_results.txt", "a") as f:
        f.write("\n=== Wyniki Scenariusza 5 ===\n")
        for rep in range(repetitions):
            f.write(f"Powtórka {rep + 1}: CPU={all_cpu_usage[rep]:.2f}%, RAM={all_ram_usage[rep]:.2f}%, "
                    f"TPS={all_tps[rep]:.2f}, Czas={all_total_times[rep]:.6f}s\n")
        f.write("\nŚrednie wartości ± Odchylenie standardowe:\n")
        f.write(f"CPU: {mean_cpu:.2f} ± {std_cpu:.2f}%\n")
        f.write(f"RAM: {mean_ram:.2f} ± {std_ram:.2f}%\n")
        f.write(f"TPS: {mean_tps:.2f} ± {std_tps:.2f}\n")
        f.write(f"Czas: {mean_total_time:.6f} ± {std_total_time:.6f}s\n")

    return mean_cpu, std_cpu, mean_ram, std_ram, mean_tps, std_tps, mean_total_time, std_total_time

def main():
    validators = [
        ValidatorInfo(name="Alicja", stake=60.0),
        ValidatorInfo(name="Bob", stake=40.0)
    ]
    pos_chain = BlockchainPoS(validators=validators)

    transactions_block1 = [
        Transaction("Alicja", "Jan", 10),
        Transaction("Jan", "Kasia", 2)
    ]
    pos_chain.add_block(transactions_block1)

    transactions_block2 = [
        Transaction("Kasia", "Zbyszek", 5),
        Transaction("Zbyszek", "Marek", 1.5)
    ]
    pos_chain.add_block(transactions_block2)

    print("=== Current PoS Blockchain ===")
    for blk in pos_chain.chain:
        print(f"Block index: {blk.index}")
        print(f"Previous hash: {blk.prev_hash}")
        print(f"Validator: {blk.validator}")
        print(f"Block hash: {blk.block_hash}")
        print(f"Transactions: {blk.transactions}")
        print("-------------------------\n")

if __name__ == "__main__":
    main()
    scenario_3_and_4_combined(repetitions=20)
    scenario_5_nothing_at_stake(repetitions=20)