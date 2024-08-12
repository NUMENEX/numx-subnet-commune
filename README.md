# NUMENEX SUBNET
## Setup project
1. Clone project
```bash
git clone https://github.com/NUMENEX/numx-subnet-commune.git
cd numx-subnet-commune
```
2. Install the required dependencies:

```bash
poetry install
```
3. Setup Wallet

Use [communex](https://github.com/agicommies/communex) cli to create wallet and make sure you fund them

```bash
comx key create key_name
```
4. Setup config file
Create `config.ini` file from `config.ini.example` with your actual key name 


## Running Miner

To run Miner, make sure you have completed the above steps from `1 to 4`
### Register Miner Module on Numenex Subnet
<mark>Remember ip and port args are for identifying miner and validator for now, you can put 0.0.0.0 for ip and 8000 for port</mark>
    ```bash
    comx module register <name> <your_commune_key> --ip <your-ip-address> --port <port> --netuid <Numenex netuid>
    ```
1. **Using User Interface:**
    ```bash
    poetry run python -m src.numenex.miner.numx
    ```
    After you have verified the server is running, please go [Here](https://github.com/NUMENEX/QA-UI) and you can start mining using our basic UI.

2. **Using CLI:**
    Checkout to feat/initial_phase and follow it's readme or go [Here](https://github.com/NUMENEX/numx-subnet-commune/tree/feat/initial_phase) and follow Readme file

## Running Validator

To run Validator, make sure you have completed the above steps from `1 to 4`
### Register Miner Module on Numenex Subnet
    ```bash
    comx module register <name> <your_commune_key> --netuid <Numenex netuid>
    ```
1. **Using User Interface:**
    ```bash
    poetry run python -m src.numenex.validator.numx
    ```
    After you have verified the server is running, please go [Here](https://github.com/NUMENEX/QA-UI) and you can start validating using our basic UI.

2. **Using CLI:**
    Checkout to feat/initial_phase and follow it's readme or go [Here](https://github.com/NUMENEX/numx-subnet-commune/tree/feat/initial_phase) and follow Readme file
