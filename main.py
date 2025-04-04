import os
import random
import asyncio
import time
from web3 import Web3
from colorama import init, Fore, Style
import aiohttp

# Initialize colorama
init(autoreset=True)

# Constants
RPC_URLS = [
    "https://testnet-rpc.monad.xyz",
    "https://monad-testnet.drpc.org"
]
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/0x"
UNISWAP_V2_ROUTER_ADDRESS = "0xCa810D095e90Daae6e867c19DF6D9A8C56db2c89"
WETH_ADDRESS = "0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701"

# List of supported tokens
TOKEN_ADDRESSES = {
    "DAC": "0x0f0bdebf0f83cd1ee3974779bcb7315f9808c714",
    "USDT": "0x88b8e2161dedc77ef4ab7585569d2415a1c1055d",
    "WETH": "0x836047a99e11f376522b447bffb6e3495dd0637c",
    "MUK": "0x989d38aeed8408452f0273c7d4a17fef20878e62",
    "USDC": "0xf817257fed379853cDe0fa4F97AB987181B1E5Ea",
    "CHOG": "0xE0590015A873bF326bd645c3E1266d4db41C4E6B"
}

# ABI for ERC20 token
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
]

# ABI for Uniswap V2 Router
ROUTER_ABI = [
    {
        "name": "swapExactETHForTokens",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}]
    },
    {
        "name": "swapExactTokensForETH",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}]
    }
]

# List of User-Agents untuk rotasi
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
]

def print_credits():
    title = "🚀 MONAD X HAHA WALLET BOT"
    author = "Author  : @Semutireng22"
    channel = "Channel : t.me/ugdairdrop"
    
    # Get terminal width
    try:
        terminal_width = os.get_terminal_size().columns
    except:
        terminal_width = 80
    
    box_width = 60
    padding = (terminal_width - box_width) // 2
    
    # Print centered box with colors
    print(" " * padding + f"{Fore.CYAN}╔{'═' * (box_width - 2)}╗{Style.RESET_ALL}")
    print(" " * padding + f"{Fore.CYAN}║{Fore.YELLOW}{title:^{box_width-2}}{Fore.CYAN}║{Style.RESET_ALL}")
    print(" " * padding + f"{Fore.CYAN}║{Fore.WHITE}{'─' * (box_width-2)}{Fore.CYAN}║{Style.RESET_ALL}")
    print(" " * padding + f"{Fore.CYAN}║{Fore.GREEN}{author:^{box_width-2}}{Fore.CYAN}║{Style.RESET_ALL}")
    print(" " * padding + f"{Fore.CYAN}║{Fore.GREEN}{channel:^{box_width-2}}{Fore.CYAN}║{Style.RESET_ALL}")
    print(" " * padding + f"{Fore.CYAN}╚{'═' * (box_width - 2)}╝{Style.RESET_ALL}")
    print()

class SwapManager:
    def __init__(self):
        print_credits()  # Add this line to show credits on startup
        self.w3 = self.connect_to_rpc()
        self.uniswap_v2_router_address = self.w3.to_checksum_address(UNISWAP_V2_ROUTER_ADDRESS)
        self.weth_address = self.w3.to_checksum_address(WETH_ADDRESS)
        self.token_addresses = {key: self.w3.to_checksum_address(value) for key, value in TOKEN_ADDRESSES.items()}
        self.config_file = 'config.txt'
        self.load_config()

    # Load config from file
    def load_config(self):
        if not os.path.exists(self.config_file):
            self.private_keys = []
            self.email = ""
            self.password = ""
            self.save_config()
        else:
            with open(self.config_file, 'r') as f:
                config = dict(line.strip().split('=', 1) for line in f if line.strip())
            self.private_keys = config.get('PRIVATE_KEYS', '').split(',') if config.get('PRIVATE_KEYS') else []
            self.email = config.get('EMAIL', '')
            self.password = config.get('PASSWORD', '')

    # Save config to file
    def save_config(self):
        with open(self.config_file, 'w') as f:
            f.write(f"PRIVATE_KEYS={','.join(self.private_keys)}\n")
            f.write(f"EMAIL={self.email}\n")
            f.write(f"PASSWORD={self.password}\n")

    # Function to login and get access token
    async def get_access_token(self):
        if not self.email or not self.password:
            print(f"{Fore.RED}❌ Email or password not found in config.txt{Style.RESET_ALL}")
            return None

        url = "https://prod.haha.me/users/login"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,id;q=0.8",
            "content-type": "application/json",
            "origin": "chrome-extension://andhndehpcjpmneneealacgnmealilal",
            "priority": "u=1, i",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "sec-fetch-storage-access": "active",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        payload = {
            "email": self.email,
            "password": self.password
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    access_token = result.get("access_token")
                    if access_token:
                        self.print_step('api', f"{Fore.GREEN}✔ Successfully logged in, access token obtained{Style.RESET_ALL}")
                        return access_token
                    else:
                        self.print_step('api', f"{Fore.RED}✘ No access token in response: {result}{Style.RESET_ALL}")
                        return None
                else:
                    self.print_step('api', f"{Fore.RED}✘ Login failed: {response.status}{Style.RESET_ALL}")
                    return None

    # Function to connect to RPC
    def connect_to_rpc(self):
        for url in RPC_URLS:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                return w3
        raise Exception(f"{Fore.RED}❌ Could not connect to any RPC{Style.RESET_ALL}")

    # Function to display pretty border
    def print_border(self, text, color=Fore.MAGENTA, width=60):
        print(f"{color}╔{'═' * (width - 2)}╗{Style.RESET_ALL}")
        print(f"{color}║{Style.RESET_ALL} {text:^56} {color}║{Style.RESET_ALL}")
        print(f"{color}╚{'═' * (width - 2)}╝{Style.RESET_ALL}")

    # Function to display step
    def print_step(self, step, message):
        steps = {'approve': 'Approve', 'swap': 'Swap', 'balance': 'Balance', 'api': 'HAHA Wallet'}
        step_text = steps[step]
        print(f"{Fore.YELLOW}🔸 {Fore.CYAN}{step_text:<15}{Style.RESET_ALL} | {message}")

    # Generate random ETH amount
    def get_random_eth_amount(self):
        return self.w3.to_wei(round(random.uniform(0.0001, 0.01), 6), 'ether')

    # Generate random delay
    def get_random_delay(self):
        return random.randint(60, 180)  # Returns seconds

    # Retry function for 429 errors
    async def retry_on_429(self, operation, max_retries=3, base_delay=2):
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if "429 Client Error" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"{Fore.YELLOW}⚠ Too many requests, retrying in {delay} seconds...{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                else:
                    raise e

    # Function to approve token
    async def approve_token(self, private_key, token_address, amount, token_symbol):
        account = self.w3.eth.account.from_key(private_key)
        wallet = account.address[:8] + "..."

        async def do_approve():
            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            balance = token_contract.functions.balanceOf(account.address).call()
            if balance < amount:
                raise ValueError(f"Insufficient {token_symbol} balance: {balance / 10**18} < {amount / 10**18}")

            self.print_step('approve', f'Approving {token_symbol}')
            tx = token_contract.functions.approve(self.uniswap_v2_router_address, amount).build_transaction({
                'from': account.address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            self.print_step('approve', f"Tx Hash: {Fore.YELLOW}{EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
            await asyncio.sleep(2)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            if receipt.status != 1:
                raise Exception(f"Approval failed: Status {receipt.status}")
            self.print_step('approve', f"{Fore.GREEN}✔ {token_symbol} approved{Style.RESET_ALL}")

        try:
            await self.retry_on_429(do_approve)
        except Exception as e:
            self.print_step('approve', f"{Fore.RED}✘ Failed: {str(e)}{Style.RESET_ALL}")
            raise

    # Function to swap MON to token
    async def swap_eth_for_tokens(self, private_key, token_address, amount_in_wei, token_symbol, auth_token):
        account = self.w3.eth.account.from_key(private_key)
        wallet = account.address[:8] + "..."

        async def do_swap():
            self.print_border(f"Swapping {self.w3.from_wei(amount_in_wei, 'ether')} MON to {token_symbol} | {wallet}", Fore.MAGENTA)
            
            mon_balance = self.w3.eth.get_balance(account.address)
            if mon_balance < amount_in_wei:
                raise ValueError(f"Insufficient MON balance: {self.w3.from_wei(mon_balance, 'ether')} < {self.w3.from_wei(amount_in_wei, 'ether')}")

            router = self.w3.eth.contract(address=self.uniswap_v2_router_address, abi=ROUTER_ABI)
            tx = router.functions.swapExactETHForTokens(
                0, [self.weth_address, token_address], account.address, int(time.time()) + 600
            ).build_transaction({
                'from': account.address,
                'value': amount_in_wei,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })

            self.print_step('swap', 'Sending...')
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            self.print_step('swap', f"Tx Hash: {Fore.YELLOW}{EXPLORER_URL}{tx_hash_hex}{Style.RESET_ALL}")
            await asyncio.sleep(2)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            
            if receipt.status == 1:
                self.print_step('swap', f"{Fore.GREEN}✔ Swap successful!{Style.RESET_ALL}")
                if auth_token:
                    onboarding_result = await self.call_set_onboarding_api(auth_token)
                    success = onboarding_result.get('data', {}).get('setOnboarding', {}).get('success', False)
                    if success:
                        await self.call_verify_transaction_api(auth_token, tx_hash_hex, account.address)
                    else:
                        self.print_step('api', f"{Fore.YELLOW}⚠ Task already completed, skipping verify transaction{Style.RESET_ALL}")
                return True
            raise Exception(f"Transaction failed: Status {receipt.status}")

        try:
            return await self.retry_on_429(do_swap)
        except Exception as e:
            self.print_step('swap', f"{Fore.RED}✘ Failed: {str(e)}{Style.RESET_ALL}")
            return False

    # Function to swap token to MON
    async def swap_tokens_for_eth(self, private_key, token_address, token_symbol, auth_token):
        account = self.w3.eth.account.from_key(private_key)
        wallet = account.address[:8] + "..."

        async def do_swap():
            self.print_border(f"Swapping {token_symbol} to MON | {wallet}", Fore.MAGENTA)
            
            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            balance = token_contract.functions.balanceOf(account.address).call()
            if balance == 0:
                self.print_step('swap', f"{Fore.BLACK}⚠ No {token_symbol}, skipping{Style.RESET_ALL}")
                return False

            await self.approve_token(private_key, token_address, balance, token_symbol)
            
            router = self.w3.eth.contract(address=self.uniswap_v2_router_address, abi=ROUTER_ABI)
            tx = router.functions.swapExactTokensForETH(
                balance, 0, [token_address, self.weth_address], account.address, int(time.time()) + 600
            ).build_transaction({
                'from': account.address,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })

            self.print_step('swap', 'Sending...')
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            self.print_step('swap', f"Tx Hash: {Fore.YELLOW}{EXPLORER_URL}{tx_hash_hex}{Style.RESET_ALL}")
            await asyncio.sleep(2)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            
            if receipt.status == 1:
                self.print_step('swap', f"{Fore.GREEN}✔ Swap successful!{Style.RESET_ALL}")
                if auth_token:
                    onboarding_result = await self.call_set_onboarding_api(auth_token)
                    success = onboarding_result.get('data', {}).get('setOnboarding', {}).get('success', False)
                    if success:
                        await self.call_verify_transaction_api(auth_token, tx_hash_hex, account.address)
                    else:
                        self.print_step('api', f"{Fore.YELLOW}⚠ Task already completed, skipping verify transaction{Style.RESET_ALL}")
                return True
            raise Exception(f"Transaction failed: Status {receipt.status}")

        try:
            return await self.retry_on_429(do_swap)
        except Exception as e:
            self.print_step('swap', f"{Fore.RED}✘ Failed: {str(e)}{Style.RESET_ALL}")
            return False

    # Function to check balance
    async def check_balance(self, private_key):
        account = self.w3.eth.account.from_key(private_key)
        wallet = account.address[:8] + "..."
        self.print_border(f"💰 Balance | {wallet}", Fore.CYAN)

        async def get_mon_balance():
            balance = self.w3.eth.get_balance(account.address)
            self.print_step('balance', f"MON: {Fore.CYAN}{self.w3.from_wei(balance, 'ether')}{Style.RESET_ALL}")

        async def get_token_balance(symbol, address):
            token_contract = self.w3.eth.contract(address=address, abi=ERC20_ABI)
            balance = token_contract.functions.balanceOf(account.address).call()
            self.print_step('balance', f"{symbol}: {Fore.CYAN}{balance / 10**18}{Style.RESET_ALL}")

        try:
            await self.retry_on_429(get_mon_balance)
            for symbol, addr in self.token_addresses.items():
                await self.retry_on_429(lambda: get_token_balance(symbol, addr))
        except Exception as e:
            self.print_step('balance', f"{Fore.RED}✘ Error reading balance: {str(e)}{Style.RESET_ALL}")

    # Fungsi untuk memanggil API setOnboarding
    async def call_set_onboarding_api(self, auth_token):
        url = "https://prod.haha.me/wallet-api/graphql"
        headers = {
            "accept": "*/*",
            "accept-language": "id,en-US;q=0.9,en;q=0.8",
            "authorization": auth_token,
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": random.choice(USER_AGENTS),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "sec-fetch-storage-access": "active",
            "x-request-source-extra": "chrome",
            "x-random-delay": str(random.randint(1, 5))
        }
        payload = {
            "operationName": None,
            "variables": {"task_id": 14},
            "query": "mutation ($task_id: Int) { setOnboarding(task_id: $task_id) { task_id success completed_all current_karma __typename } }"
        }

        async with aiohttp.ClientSession() as session:
            await asyncio.sleep(random.uniform(1, 3))
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    success = result.get('data', {}).get('setOnboarding', {})
                    karma = success.get('current_karma', 0)
                    if success.get('success', False):
                        self.print_step('api', f"{Fore.GREEN}✔ Task completed! Karma: {karma}{Style.RESET_ALL}")
                    else:
                        self.print_step('api', f"{Fore.YELLOW}⚠ Daily limit reached! Current karma: {karma}{Style.RESET_ALL}")
                    return result
                else:
                    self.print_step('api', f"{Fore.RED}✘ API Error: {response.status}{Style.RESET_ALL}")
                    return None

    async def call_verify_transaction_api(self, auth_token, tx_hash, wallet_address):
        url = "https://prod.haha.me/wallet-api/graphql"
        headers = {
            "accept": "*/*",
            "accept-language": "id,en-US;q=0.9,en;q=0.8",
            "authorization": auth_token,
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": random.choice(USER_AGENTS),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "sec-fetch-storage-access": "active",
            "x-request-source-extra": "chrome",
            "x-random-delay": str(random.randint(1, 5))
        }
        payload = {
            "operationName": None,
            "variables": {
                "platformId": -10143,
                "hash": tx_hash,
                "walletAddress": wallet_address
            },
            "query": "mutation ($hash: String!, $platformId: Int!, $walletAddress: String!) { verifyTransaction(platformId: $platformId hash: $hash walletAddress: $walletAddress) }"
        }

        async with aiohttp.ClientSession() as session:
            await asyncio.sleep(random.uniform(1, 3))
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    success = result.get('data', {}).get('verifyTransaction', False)
                    if success:
                        self.print_step('api', f"{Fore.GREEN}✔ Transaction verified{Style.RESET_ALL}")
                    else:
                        self.print_step('api', f"{Fore.YELLOW}⚠ Verification skipped{Style.RESET_ALL}")
                else:
                    self.print_step('api', f"{Fore.RED}✘ API Error: {response.status}{Style.RESET_ALL}")

    # Run swap cycle for each private key
    async def run_swap_cycle(self, cycles, auth_token):
        if not self.private_keys:
            print(f"{Fore.RED}❌ No private keys found in config.txt{Style.RESET_ALL}")
            return

        for account_idx, private_key in enumerate(self.private_keys, 1):
            wallet = self.w3.eth.account.from_key(private_key).address[:8] + "..."
            self.print_border(f"🏦 ACCOUNT {account_idx}/{len(self.private_keys)} | {wallet}", Fore.BLUE)
            await self.check_balance(private_key)

            for i in range(cycles):
                self.print_border(f"🔄 UNISWAP SWAP CYCLE {i + 1}/{cycles} | {wallet}", Fore.CYAN)
                
                # Swap MON to tokens
                for token_symbol, token_address in self.token_addresses.items():
                    eth_amount = self.get_random_eth_amount()
                    await self.swap_eth_for_tokens(private_key, token_address, eth_amount, token_symbol, auth_token)
                    await asyncio.sleep(5)

                # Swap tokens back to MON
                self.print_border(f"🔄 SWAP ALL TOKENS BACK TO MON | {wallet}", Fore.CYAN)
                for token_symbol, token_address in self.token_addresses.items():
                    await self.swap_tokens_for_eth(private_key, token_address, token_symbol, auth_token)
                    await asyncio.sleep(5)

                if i < cycles - 1:
                    delay = self.get_random_delay()
                    print(f"\n{Fore.YELLOW}⏳ Waiting {delay / 60:.1f} minutes before next cycle...{Style.RESET_ALL}")
                    await asyncio.sleep(delay)

            if account_idx < len(self.private_keys):
                delay = self.get_random_delay()
                print(f"\n{Fore.YELLOW}⏳ Waiting {delay / 60:.1f} minutes before next account...{Style.RESET_ALL}")
                await asyncio.sleep(delay)

        print(f"{Fore.GREEN}{'═' * 60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}│ ALL DONE: {cycles} CYCLES FOR {len(self.private_keys)} ACCOUNTS{' ' * (32 - len(str(cycles)) - len(str(len(self.private_keys))))}│{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'═' * 60}{Style.RESET_ALL}")

    # Main function
    async def run(self):
        # Dapatkan access token
        auth_token = await self.get_access_token()
        if not auth_token:
            print(f"{Fore.RED}❌ Failed to obtain access token, exiting...{Style.RESET_ALL}")
            return

        if not self.private_keys:
            print(f"{Fore.RED}❌ No private keys found in config.txt, exiting...{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}👥 Accounts: {len(self.private_keys)}{Style.RESET_ALL}")

        while True:
            try:
                self.print_border("🔢 NUMBER OF CYCLES", Fore.YELLOW)
                cycles_input = input(f"{Fore.GREEN}➤ Enter number of cycles (default 5): {Style.RESET_ALL}")
                cycles = int(cycles_input) if cycles_input.strip() else 5
                if cycles <= 0:
                    raise ValueError
                break
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number!{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}🚀 Running {cycles} Uniswap swap cycles with random 1-3 minute delay for {len(self.private_keys)} accounts...{Style.RESET_ALL}")
        await self.run_swap_cycle(cycles, auth_token)

if __name__ == "__main__":
    swap_manager = SwapManager()
    asyncio.run(swap_manager.run())