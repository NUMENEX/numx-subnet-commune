
# NUMENEX SUBNET

## Setup Project

1. Clone project

```bash
git clone git@github.com:NUMENEX/numx-subnet-commune.git
```

2. Install the required dependencies:

    ```bash
    poetry install
    ```

## Setup Wallet

Use [communex](https://github.com/agicommies/communex) package to create wallet

```bash
comx key create key_name
```

## Setup config file
Create 
```bash
config.ini
```
file from config.ini.example with your actual key name 


## Running the Miner

After completing above steps

Run the miner:

    ```bash
    poetry run python -m src.numenex.miner.trade
    ```

## Running the Validator
Complete all above steps before you run validator
Run the validator:

    ```bash
    poetry run python -m src.numenex.cli
    ```