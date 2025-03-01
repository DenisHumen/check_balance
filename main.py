import time
import csv
import inquirer
from config.rpc import L1, base, sepolia, arbitrum, optimism, soneium, Polygon, Binance_Smart_Chain, Avalanche, Fantom, Gravity_Alpha_Mainnet
from config.config import NUM_THREADS
from colorama import Fore, init
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# импорт функций из модулей
from modules.get_wallet_balance import get_wallet_balance
from modules.get_wallet_balance_fast import get_wallet_balance_fast
from modules.get_gas_price import get_gas_price
from modules.sum_balances import sum_balances
from modules.get_transaction_count import get_transaction_count

init(autoreset=True)

rpc_urls = {
    '🚀 Sepolia': sepolia,
    '🚀 Ethereum Mainnet': L1,
    '🚀 Base': base,
    '🚀 Arbitrum One': arbitrum,
    '🚀 Optimism': optimism,
    '🚀 Soneium': soneium,
    '🚀 Polygon': Polygon,
    '🚀 Binance Smart Chain': Binance_Smart_Chain,
    '🚀 Avalanche': Avalanche,
    '🚀 Fantom': Fantom,
    '🚀 Gravity Alpha Mainnet': Gravity_Alpha_Mainnet
}

def main_menu():
    try:
        while True:
            questions = [
                inquirer.List('action',
                              message="What do you want to do?",
                              choices=['💲 Check Balances', '💰 Sum Balances', '⛽ Check Gas Price', '🔢 Check Transaction Count', '❌ Exit'],
                             ),
                inquirer.List('network',
                              message="Which network do you want to check?",
                              choices=list(rpc_urls.keys()) + ['🔙 Back'],
                             ),
            ]
            answers = inquirer.prompt(questions)
            action = answers['action']
            network = answers['network']

            if action == '❌ Exit' or network == '🔙 Back':
                break
            elif action == '💰 Sum Balances':
                sum_balances('result/result.csv')
            elif action == '💲 Check Balances':
                check_balances_menu(network)
            elif action == '⛽ Check Gas Price':
                check_gas_price_menu(network)
            elif action == '🔢 Check Transaction Count':
                check_transaction_count_menu(network)
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def check_balances_menu(network):
    try:
        questions = [
            inquirer.List('mode',
                          message="Select mode:",
                          choices=['🚀 Fast (requires proxies)', '🐢 Slow (no proxies)'],
                         ),
        ]
        answers = inquirer.prompt(questions)
        mode = answers['mode']

        with open('walletss.txt', 'r', encoding='utf-8') as file:
            wallet_addresses = file.readlines()

        if mode == '🚀 Fast (requires proxies)':
            check_balances_fast(wallet_addresses, network, random.choice(rpc_urls[network]))
        else:
            check_balances_slow(wallet_addresses, network, random.choice(rpc_urls[network]))
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def check_balances_fast(wallet_addresses, network, rpc_url):
    try:
        with open('proxy.csv', 'r', encoding='utf-8') as file:
            proxies = file.readlines()[1:]

        if len(proxies) < len(wallet_addresses):
            print(Fore.YELLOW + "WARNING: Так как прокси меньше кошельков, будут браться рандомно.")
        else:
            print(Fore.GREEN + "INFO: Прокси больше или равны количеству кошельков, будет использоваться 1к1.")

        with open('result/result.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['address', 'balance', 'network']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                future_to_address = {executor.submit(get_wallet_balance_fast, addr.strip(), rpc_url, proxies): addr for addr in wallet_addresses}
                for future in tqdm(as_completed(future_to_address), total=len(wallet_addresses), desc="Checking balances", unit="wallet"):
                    address = future_to_address[future]
                    try:
                        balance = future.result()
                        if balance is not None:
                            writer.writerow({'address': address.strip(), 'balance': balance, 'network': network})
                        else:
                            writer.writerow({'address': address.strip(), 'balance': 'N/A', 'network': network})
                    except Exception as e:
                        print(Fore.RED + f"Error checking balance for {address.strip()}: {e}")
                        writer.writerow({'address': address.strip(), 'balance': 'N/A', 'network': network})

        print(Fore.GREEN + f"\n\n\nBalances checked and saved in result/result.csv for {network} network\n")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def check_balances_slow(wallet_addresses, network, rpc_url):
    try:
        with open('result/result.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['address', 'balance', 'network']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for address in tqdm(wallet_addresses, desc="Checking balances", unit="wallet"):
                address = address.strip()
                balance = get_wallet_balance(address, rpc_url)
                time.sleep(1)
                writer.writerow({'address': address, 'balance': balance, 'network': network})

        print(Fore.GREEN + f"\n\n\nBalances checked and saved in result/result.csv for {network} network\n")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def check_gas_price_menu(network):
    try:
        gas_price = get_gas_price(random.choice(rpc_urls[network]))
        if gas_price is not None:
            print(Fore.GREEN + f"\n\n\n⛽ Current gas price on {network}: {gas_price} Gwei\n")
        else:
            print(Fore.RED + f"\n\n\n❌ Failed to retrieve gas price for {network}.\n")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def check_transaction_count_menu(network):
    try:
        with open('walletss.txt', 'r', encoding='utf-8') as file:
            wallet_addresses = file.readlines()

        with open('result/transaction_count_result.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['address', 'transaction_count', 'network']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for address in tqdm(wallet_addresses, desc="Checking transaction counts", unit="wallet"):
                address = address.strip()
                count = get_transaction_count(address, random.choice(rpc_urls[network]))
                time.sleep(1)
                writer.writerow({'address': address, 'transaction_count': count, 'network': network})

        print(Fore.GREEN + f"\n\n\nTransaction counts checked and saved in result/transaction_count_result.csv for {network} network\n")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

if __name__ == "__main__":
    main_menu()

