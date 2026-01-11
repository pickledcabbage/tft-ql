import yaml

with open("config/config.yaml", "r") as file:
    _config_file = yaml.safe_load(file)
print("Loaded config", _config_file)

# Server configs.
DB = "mongodb://127.0.0.1:32769/?directConnection=true"
IP = "0.0.0.0"
PORT = 10000

# Alias configs.
CHAMP_ALIAS_FILE = "config/champ_aliases.csv"
ITEM_ALIAS_FILE = "config/item_aliases.csv"
TRAIT_ALIAS_FILE = "config/trait_aliases.csv"
