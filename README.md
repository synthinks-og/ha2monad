# MONAD X HAHA WALLET BOT

## Introduction
MONAD TESTNET X Haha Wallet is a BOT designed to help users automatically run the Monad Testnet and Haha Wallet testnet.


### Configuration
Before running the program, you need to configure the `config.txt` file with the following information:

1. Create a HAHA wallet account through the referral link: https://join.haha.me/SLAMET-VS3MDA
2. Edit the `config.txt` file and fill it with the following format:
```
PRIVATE_KEYS=your_wallet_private_key
EMAIL=your_haha_wallet_email
PASSWORD=your_haha_wallet_password
```

Example:
```
PRIVATE_KEYS=0x1234...abcd
EMAIL=example@email.com
PASSWORD=YourSecurePassword123
```
Or you can use this terminal command to edit the file with your preferred text editor. Replace `nano` with your preferred editor (e.g., `vim` or `gedit`):
```
nano config.txt
```
**IMPORTANT:** Keep your credential information secure. Never share your private key, email, and password with anyone.

## Installation and Usage on Linux/Ubuntu

### Clone Repository
```bash
git clone https://github.com/Semutireng22/ha2monad.git
cd ha2monad
```

### Install Python and Dependencies
```bash
python3 --version
```
If Python is not installed, install it with:
```bash
sudo apt update
sudo apt install python3-pip
```

```bash
pip install -r requirements.txt
```

### Running the Program
```bash
python3 main.py
```

## Installation and Usage on Windows PowerShell

### Clone Repository
```powershell
git clone https://github.com/Semutireng22/ha2monad.git
cd ha2monad
```

### Install Python and Dependencies

Download and install Python from python.org. Make sure Python is installed by running:
```powershell
python --version
```
If Python is installed, proceed with:
```powershell
pip install -r requirements.txt
```

### Running the Program
```powershell
python3 main.py
```

## Installation and Usage on Termux Android

### Initial Setup
```bash
pkg update && pkg upgrade
pkg install python git
```

### Clone Repository
```bash
git clone https://github.com/Semutireng22/ha2monad.git
cd ha2monad
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Running the Program
```bash
python main.py
```

## Credit
This program was developed by @Semutireng22

Join our Telegram channel for the latest updates: [t.me/ugdairdrop](https://t.me/ugdairdrop)

Thank you to all contributors who have helped in developing this bot.