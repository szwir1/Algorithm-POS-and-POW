import time
import matplotlib.pyplot as plt
import statistics   
import psutil       
import threading
import random

from blockchain import Blockchain, save_blockchain_to_file
from block import Block
from transaction import Transaction

def measure_and_plot_difficulty(difficulties):
    times = []
    print("\n=== Pomiar czasu kopania bloku przy różnych poziomach trudności ===")
    with open("results.txt", "a") as f:
        f.write("=== Pomiar czasu kopania bloku przy różnych poziomach trudności ===\n")
    
    for diff in difficulties:
        print(f"  Kopanie testowego bloku z difficulty={diff}...")
        test_block = Block(index=999, prev_hash="XYZ", difficulty=diff, use_multiprocessing=False)
        
        start_t = time.time()
        test_block.mine_block()
        end_t = time.time()
        
        elapsed = end_t - start_t
        times.append(elapsed)
        print(f"  Czas kopania (difficulty={diff}): {elapsed:.2f} s")
        
        with open("results.txt", "a") as f:
            f.write(f"Difficulty={diff}: Czas kopania: {elapsed:.2f} s\n")

    # wykres
    plt.plot(difficulties, times, marker='o')
    plt.title("Czas kopania bloku vs. poziom trudności (liczba zer)")
    plt.xlabel("Trudność (liczba zer)")
    plt.ylabel("Czas [s]")
    plt.show()

    with open("results.txt", "a") as f:
        f.write("-------------------\n")

    return times

def monitor_resources(process, stop_monitoring, cpu_measurements, ram_measurements):
    """
    Funkcja monitorująca zużycie CPU i RAM w osobnym wątku.
    """
    process.cpu_percent(interval=None)
    for child in process.children(recursive=True):
        try:
            child.cpu_percent(interval=0.1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    while not stop_monitoring.is_set():
        children = process.children(recursive=True)
        cpu_total = process.cpu_percent(interval=0.1)
        ram_total = process.memory_info().rss / 1024 / 1024
        for child in children:
            try:
                cpu_total += child.cpu_percent(interval=0.1)
                ram_total += child.memory_info().rss / 1024 / 1024
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        cpu_measurements.append(cpu_total)
        ram_measurements.append(ram_total)
        time.sleep(0.1)

def main():
    DIFFICULTY = 3
    NUM_BLOCKS = 20
    print(f"\n=== Tworzenie łańcucha z difficulty={DIFFICULTY} (liczba bloków: {NUM_BLOCKS}) ===")
    with open("results.txt", "a") as f:
        f.write(f"\n=== Tworzenie łańcucha z difficulty={DIFFICULTY} (liczba bloków: {NUM_BLOCKS}) ===\n")

    my_chain = Blockchain(difficulty=DIFFICULTY)

    block_times = []
    cpu_usage = []
    ram_usage = []
    process = psutil.Process()

    start_chain_time = time.time()
    for i in range(1, NUM_BLOCKS + 1):
        start_block = time.time()
        block = Block(index=i, difficulty=DIFFICULTY, use_multiprocessing=False)
        block.transactions.append(Transaction("Nastja", "Igor", 10*i))
        block.transactions.append(Transaction("Igor", "Andrzej", 5*i))

        cpu_measurements = []
        ram_measurements = []
        stop_monitoring = threading.Event()
        monitor_thread = threading.Thread(
            target=monitor_resources,
            args=(process, stop_monitoring, cpu_measurements, ram_measurements)
        )
        monitor_thread.start()

        my_chain.add_block(block)

        stop_monitoring.set()
        monitor_thread.join()

        end_block = time.time()
        elapsed_block = end_block - start_block
        block_times.append(elapsed_block)

        cpu_avg = statistics.mean(cpu_measurements) if cpu_measurements else 0.0
        ram_avg = statistics.mean(ram_measurements) if ram_measurements else 0.0
        cpu_usage.append(cpu_avg)
        ram_usage.append(ram_avg)

        print(f"[Block {i}] Wykopany w {elapsed_block:.3f} s, CPU: {cpu_avg:.1f}%, RAM: {ram_avg:.1f} MB")
        with open("results.txt", "a") as f:
            f.write(f"[Block {i}] Wykopany w {elapsed_block:.3f} s, CPU: {cpu_avg:.1f}%, RAM: {ram_avg:.1f} MB\n")

    end_chain_time = time.time()
    total_chain_time = end_chain_time - start_chain_time

    mean_time = statistics.mean(block_times)
    stdev_time = statistics.stdev(block_times) if len(block_times) > 1 else 0.0
    mean_cpu = statistics.mean(cpu_usage)
    stdev_cpu = statistics.stdev(cpu_usage) if len(cpu_usage) > 1 else 0.0
    mean_ram = statistics.mean(ram_usage)
    stdev_ram = statistics.stdev(ram_usage) if len(ram_usage) > 1 else 0.0

    print(f"\n=== Zakończono kopanie {NUM_BLOCKS} bloków w {total_chain_time:.2f} s (difficulty={DIFFICULTY}) ===")
    print(f"    Średni czas 1 bloku: {mean_time:.3f} s  (±{stdev_time:.3f} s)")
    print(f"    Średnie zużycie CPU: {mean_cpu:.1f}% (±{stdev_cpu:.1f}%)")
    print(f"    Średnie zużycie RAM: {mean_ram:.1f} MB (±{stdev_ram:.1f} MB)")

    with open("results.txt", "a") as f:
        f.write(f"\nZakończono kopanie {NUM_BLOCKS} bloków w {total_chain_time:.2f} s (difficulty={DIFFICULTY})\n")
        f.write(f"Średni czas 1 bloku: {mean_time:.3f} s (±{stdev_time:.3f} s)\n")
        f.write(f"Średnie zużycie CPU: {mean_cpu:.1f}% (±{stdev_cpu:.1f}%)\n")
        f.write(f"Średnie zużycie RAM: {mean_ram:.1f} MB (±{stdev_ram:.1f} MB)\n")

    print("\n=== Zapisujemy łańcuch do pliku chain_data.json ===")
    save_blockchain_to_file(my_chain.chain, filename="chain_data.json")

    print("\n=== Aktualny stan łańcucha ===")
    with open("results.txt", "a") as f:
        f.write("\nAktualny stan łańcucha:\n")
    for blk in my_chain.chain:
        print(f"Block index: {blk.index}")
        print(f"Previous hash: {blk.prev_hash}")
        print(f"Block hash: {blk.block_hash}")
        print(f"Nonce: {blk.nonce}")
        print(f"Attempts: {blk.attempts}")
        print(f"Transactions: {blk.transactions}")
        print("-------------------------")
        with open("results.txt", "a") as f:
            f.write(f"Block index: {blk.index}\n")
            f.write(f"Previous hash: {blk.prev_hash}\n")
            f.write(f"Block hash: {blk.block_hash}\n")
            f.write(f"Nonce: {blk.nonce}\n")
            f.write(f"Attempts: {blk.attempts}\n")
            f.write(f"Transactions: {blk.transactions}\n")
            f.write("-------------------------\n")
    
    with open("results.txt", "a") as f:
        f.write("-------------------\n")

def scenario_4_transaction_load(num_runs=20):
    DIFFICULTY = 4
    NUM_BLOCKS = 50
    TRANSACTIONS_PER_BLOCK = 100
    results = []

    for run in range(num_runs):
        print(f"\n=== Scenariusz 4, Uruchomienie {run+1}/{num_runs}: Obciążenie dużą liczbą transakcji (PoW, difficulty={DIFFICULTY}) ===")
        with open("results.txt", "a") as f:
            f.write(f"\n=== Scenariusz 4, Uruchomienie {run+1}/{num_runs}: Obciążenie dużą liczbą transakcji (PoW, difficulty={DIFFICULTY}) ===\n")

        my_chain = Blockchain(difficulty=DIFFICULTY)

        mempool = []
        for i in range(1000):
            sender = f"User_{random.randint(1, 100)}"
            receiver = f"User_{random.randint(1, 100)}"
            amount = random.uniform(0.1, 10.0)
            mempool.append(Transaction(sender, receiver, amount))

        total_time = 0.0
        process = psutil.Process()
        cpu_usage = []
        ram_usage = []

        for i in range(1, NUM_BLOCKS + 1):
            block_transactions = mempool[(i-1) * TRANSACTIONS_PER_BLOCK:i * TRANSACTIONS_PER_BLOCK]
            start_block = time.time()
            block = Block(index=i, difficulty=DIFFICULTY, use_multiprocessing=False)
            block.transactions = block_transactions

            cpu_measurements = []
            ram_measurements = []
            stop_monitoring = threading.Event()
            monitor_thread = threading.Thread(
                target=monitor_resources,
                args=(process, stop_monitoring, cpu_measurements, ram_measurements)
            )
            monitor_thread.start()

            my_chain.add_block(block)

            stop_monitoring.set()
            monitor_thread.join()

            end_block = time.time()
            block_time = end_block - start_block
            total_time += block_time

            cpu_avg = statistics.mean(cpu_measurements) if cpu_measurements else 0.0
            ram_avg = statistics.mean(ram_measurements) if ram_measurements else 0.0
            cpu_usage.append(cpu_avg)
            ram_usage.append(ram_avg)

            print(f"[Block {i}] Wykopany w {block_time:.3f} s, CPU: {cpu_avg:.1f}%, RAM: {ram_avg:.1f} MB")
            with open("results.txt", "a") as f:
                f.write(f"[Block {i}] Wykopany w {block_time:.3f} s, CPU: {cpu_avg:.1f}%, RAM: {ram_avg:.1f} MB\n")

        total_transactions = 1000
        tps = total_transactions / total_time if total_time > 0 else 0
        mean_cpu = statistics.mean(cpu_usage)
        mean_ram = statistics.mean(ram_usage)

        print(f"\nŁączny czas przetwarzania {NUM_BLOCKS} bloków: {total_time:.3f} s")
        print(f"Przepustowość (TPS): {tps:.2f}")
        print(f"Średnie zużycie CPU: {mean_cpu:.1f}%")
        print(f"Średnie zużycie RAM: {mean_ram:.1f} MB")

        with open("results.txt", "a") as f:
            f.write(f"\nŁączny czas przetwarzania {NUM_BLOCKS} bloków: {total_time:.3f} s\n")
            f.write(f"Przepustowość (TPS): {tps:.2f}\n")
            f.write(f"Średnie zużycie CPU: {mean_cpu:.1f}%\n")
            f.write(f"Średnie zużycie RAM: {mean_ram:.1f} MB\n")

        results.append({
            "run": run + 1,
            "total_time": total_time,
            "tps": tps,
            "mean_cpu": mean_cpu,
            "mean_ram": mean_ram
        })

    # obliczam statystyki
    total_times = [r["total_time"] for r in results]
    tps_values = [r["tps"] for r in results]
    cpu_values = [r["mean_cpu"] for r in results]
    ram_values = [r["mean_ram"] for r in results]

    mean_total_time = statistics.mean(total_times)
    stdev_total_time = statistics.stdev(total_times) if len(total_times) > 1 else 0.0
    mean_tps = statistics.mean(tps_values)
    stdev_tps = statistics.stdev(tps_values) if len(tps_values) > 1 else 0.0
    mean_cpu = statistics.mean(cpu_values)
    stdev_cpu = statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0.0
    mean_ram = statistics.mean(ram_values)
    stdev_ram = statistics.stdev(ram_values) if len(ram_values) > 1 else 0.0

    print("\n=== Statystyki dla Scenariusza 4 ===")
    print(f"Średni czas: {mean_total_time:.3f} s (±{stdev_total_time:.3f} s)")
    print(f"Średni TPS: {mean_tps:.2f} (±{stdev_tps:.2f})")
    print(f"Średnie zużycie CPU: {mean_cpu:.1f}% (±{stdev_cpu:.1f}%)")
    print(f"Średnie zużycie RAM: {mean_ram:.1f} MB (±{stdev_ram:.1f} MB)")

    with open("results.txt", "a") as f:
        f.write("\n=== Statystyki dla Scenariusza 4 ===\n")
        f.write(f"Średni czas: {mean_total_time:.3f} s (±{stdev_total_time:.3f} s)\n")
        f.write(f"Średni TPS: {mean_tps:.2f} (±{stdev_tps:.2f})\n")
        f.write(f"Średnie zużycie CPU: {mean_cpu:.1f}% (±{stdev_cpu:.1f}%)\n")
        f.write(f"Średnie zużycie RAM: {mean_ram:.1f} MB (±{stdev_ram:.1f} MB)\n")
        f.write("-------------------\n")

def scenario_5_51_percent_attack(num_runs=20):
    DIFFICULTY = 4
    NUM_BLOCKS = 100
    results = []

    for run in range(num_runs):
        print(f"\n=== Scenariusz 5, Uruchomienie {run+1}/{num_runs}: Atak 51% (PoW, difficulty={DIFFICULTY}) ===")
        with open("results.txt", "a") as f:
            f.write(f"\n=== Scenariusz 5, Uruchomienie {run+1}/{num_runs}: Atak 51% (PoW, difficulty={DIFFICULTY}) ===\n")

        nodes = {
            "Honest": 0.4,
            "Attacker": 0.6
        }
        my_chain = Blockchain(difficulty=DIFFICULTY)

        block_counts = {"Honest": 0, "Attacker": 0}
        process = psutil.Process()
        cpu_usage = []
        ram_usage = []

        for i in range(1, NUM_BLOCKS + 1):
            chosen_node = random.choices(
                list(nodes.keys()),
                weights=list(nodes.values()),
                k=1
            )[0]

            start_block = time.time()
            block = Block(index=i, difficulty=DIFFICULTY, use_multiprocessing=False)
            block.transactions.append(Transaction("User1", "User2", 10*i))

            cpu_measurements = []
            ram_measurements = []
            stop_monitoring = threading.Event()
            monitor_thread = threading.Thread(
                target=monitor_resources,
                args=(process, stop_monitoring, cpu_measurements, ram_measurements)
            )
            monitor_thread.start()

            my_chain.add_block(block)

            stop_monitoring.set()
            monitor_thread.join()

            end_block = time.time()
            block_time = end_block - start_block

            block_counts[chosen_node] += 1

            cpu_avg = statistics.mean(cpu_measurements) if cpu_measurements else 0.0
            ram_avg = statistics.mean(ram_measurements) if ram_measurements else 0.0
            cpu_usage.append(cpu_avg)
            ram_usage.append(ram_avg)

            print(f"[Block {i}] Wykopany przez {chosen_node} w {block_time:.3f} s, CPU: {cpu_avg:.1f}%, RAM: {ram_avg:.1f} MB")
            with open("results.txt", "a") as f:
                f.write(f"[Block {i}] Wykopany przez {chosen_node} w {block_time:.3f} s, CPU: {cpu_avg:.1f}%, RAM: {ram_avg:.1f} MB\n")

        print("\n--- Analiza ataku 51% ---")
        with open("results.txt", "a") as f:
            f.write("\nAnaliza ataku 51%:\n")
        for node, count in block_counts.items():
            percentage = (count / NUM_BLOCKS) * 100
            print(f"Węzeł {node}: Wygenerował {count} bloków ({percentage:.2f}%)")
            with open("results.txt", "a") as f:
                f.write(f"Węzeł {node}: Wygenerował {count} bloków ({percentage:.2f}%)\n")

        mean_cpu = statistics.mean(cpu_usage)
        mean_ram = statistics.mean(ram_usage)
        print(f"Średnie zużycie CPU: {mean_cpu:.1f}%")
        print(f"Średnie zużycie RAM: {mean_ram:.1f} MB")
        with open("results.txt", "a") as f:
            f.write(f"Średnie zużycie CPU: {mean_cpu:.1f}%\n")
            f.write(f"Średnie zużycie RAM: {mean_ram:.1f} MB\n")

        results.append({
            "run": run + 1,
            "block_counts": block_counts,
            "mean_cpu": mean_cpu,
            "mean_ram": mean_ram
        })

    # obliczm statystyki
    honest_counts = [r["block_counts"]["Honest"] for r in results]
    attacker_counts = [r["block_counts"]["Attacker"] for r in results]
    cpu_values = [r["mean_cpu"] for r in results]
    ram_values = [r["mean_ram"] for r in results]

    mean_honest = statistics.mean(honest_counts)
    stdev_honest = statistics.stdev(honest_counts) if len(honest_counts) > 1 else 0.0
    mean_attacker = statistics.mean(attacker_counts)
    stdev_attacker = statistics.stdev(attacker_counts) if len(attacker_counts) > 1 else 0.0
    mean_cpu = statistics.mean(cpu_values)
    stdev_cpu = statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0.0
    mean_ram = statistics.mean(ram_values)
    stdev_ram = statistics.stdev(ram_values) if len(ram_values) > 1 else 0.0

    print("\n=== Statystyki dla Scenariusza 5 ===")
    print(f"Średnia liczba bloków Honest: {mean_honest:.1f} (±{stdev_honest:.1f})")
    print(f"Średnia liczba bloków Attacker: {mean_attacker:.1f} (±{stdev_attacker:.1f})")
    print(f"Średnie zużycie CPU: {mean_cpu:.1f}% (±{stdev_cpu:.1f}%)")
    print(f"Średnie zużycie RAM: {mean_ram:.1f} MB (±{stdev_ram:.1f} MB)")

    with open("results.txt", "a") as f:
        f.write("\n=== Statystyki dla Scenariusza 5 ===\n")
        f.write(f"Średnia liczba bloków Honest: {mean_honest:.1f} (±{stdev_honest:.1f})\n")
        f.write(f"Średnia liczba bloków Attacker: {mean_attacker:.1f} (±{stdev_attacker:.1f})\n")
        f.write(f"Średnie zużycie CPU: {mean_cpu:.1f}% (±{stdev_cpu:.1f}%)\n")
        f.write(f"Średnie zużycie RAM: {mean_ram:.1f} MB (±{stdev_ram:.1f} MB)\n")
        f.write("-------------------\n")

    # wykres na podstawie srednich 
    plt.bar(["Honest", "Attacker"], [mean_honest, mean_attacker], yerr=[stdev_honest, stdev_attacker], capsize=5, color=['blue', 'red'])
    plt.title("Scenariusz 5: Średnia liczba bloków wygenerowanych przez węzły (Atak 51%)")
    plt.xlabel("Węzeł")
    plt.ylabel("Liczba bloków")
    plt.show()

if __name__ == "__main__":
    # czyscimy pli 
    with open("results.txt", "w") as f:
        f.write("")

    #  test measure_and_plot_difficulty wykres z poziomem trudnosci
    DO_MEASURE = True
    if DO_MEASURE:
        DIFFS = [1, 2, 3, 4, 5, 6]
        measure_and_plot_difficulty(DIFFS)

    # mierzymy czxas kopania i zasoby 
    main()

    # 1000 transakcji 
    scenario_4_transaction_load(num_runs=20)

    # atak 51% 
    scenario_5_51_percent_attack(num_runs=20)