# NUMENEX
What is Numenex?
Numenex creates a network of competitive transaction markets, which facilitates the deployment of AI Digital Twins across a multitude of applications. These applications include Futures Trading Decentralized Exchanges (DEX), marketplaces for digital assets, copy trading functionalities that allow users to mimic successful trading strategies, and Predictive Token Analytics that utilize AI to forecast token performance. The platform will provide Market Positioning Business Intelligence, helping businesses make informed decisions and strategize effectively in the crypto market.

Currently we are on phase one: Data collection phase
In order to understand the sentiment and train the models accordingly, we are collecting the sentiment of people as data.
The task for the miner is:
There will be bunch of questions ( for now we refresh it every 8 hours)
Miner need to answer those questions with supporting resources for each questions so that validator can give miner higher scores

The task for validator is:
Validator needs to score the miner depending upon the answer and resources they provided and after the miners are scored and weighted, the data are stored in our db as well as we update it into our huggingface repo which is currently on developement.

Let's grow together with #NUMENEX

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

5. Register Miner/Validtor Module on Numenex Subnet

    **Registering Miner**
    
    <mark>Remember ip and port args are for identifying miner and validator for now, you can put 127.0.0.1 for ip and 8000 for port</mark>

    ```bash
    comx module register <name> <your_commune_key> --ip <your-ip-address> --port <port> --netuid <Numenex netuid>
    ```
    **Registering Validator**
    
    ```bash
    comx module register <name> <your_commune_key> --netuid <Numenex netuid>
    ```
    


## Running Miner

To run Miner, make sure you have completed the above steps from `1 to 5`
1. **Using User Interface:**
    ```bash
    poetry shell
    ```
    ```bash
    poetry run python -m src.numenex.miner.numx
    ```
    After you have verified the server is running, please go [Here](https://github.com/NUMENEX/QA-UI) and you can start mining using our basic UI.

2. **Using CLI:**
    Checkout to feat/initial_phase and follow it's readme or go [Here](https://github.com/NUMENEX/numx-subnet-commune/tree/feat/initial_phase) and follow Readme file

**Note For Miners**
1. Please provide valid website links that are not paywalled. If you do not provide webpage links, you will not be rewarded
2. Use website that is at least 1 year old
3. Do not use paywalled or blogpost websites

## Running Validator

To run Validator, make sure you have completed the above steps from `1 to 5`
1. Get `OpenAi Api key and api ninja api key` and update it in `config.ini` file

2. - Executing scripts directly
    ```bash
    poetry shell
    ```
    ```bash
    poetry run python -m src.numenex.validator.numx
    ```
    - Using [PM2](https://pm2.keymetrics.io/docs/usage/quick-start/)
        - Run using config file
        ```bash
        pm2 start ./ecosystem.config.js
        ```
        - Run using cli
        ```bash
        pm2 start --name numenex-vali --interpreter bash -- "poetry" "run" "python" "-m" "src.numenex.validator.numx" --no-vizion
        ```
    

