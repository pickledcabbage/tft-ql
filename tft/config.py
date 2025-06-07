import yaml

with open("config/config.yaml", "r") as file:
    _config_file = yaml.safe_load(file)
print("Loaded config", _config_file)

# Server configs.
DB = _config_file['backend']['db']
IP = _config_file['backend']['ip']
PORT = _config_file['backend']['port']

# Alias configs.
CHAMP_ALIAS_FILE = _config_file['files']['champ_alias']
ITEM_ALIAS_FILE = _config_file['files']['item_alias']
TRAIT_ALIAS_FILE = _config_file['files']['trait_alias']