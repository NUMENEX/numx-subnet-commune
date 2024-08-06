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

```bash
poetry run python -m src.numenex.miner.numx [options]
```
There are two options, `get_questions` and `answer_questions`
There are examples given in code please go through it.

## Running Validator

To run Validator, make sure you have completed the above steps from `1 to 4`

```bash
poetry run python -m src.numenex.validator.numx [options]
```
There are two options, `get_answers` and `validate_and_update_answers`
There are examples given in code please go through it.
