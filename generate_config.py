import json
import getpass

CONFIG_FILE = 'db_config.json'

def create_config_file():
    config = {
        'host': 'localhost',
        'user': input("Enter MySQL username: "),
        'password': getpass.getpass("Enter MySQL password: "),
        'database': 'leetcodereview'
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)
    print(f"Configuration file '{CONFIG_FILE}' created successfully.")

if __name__ == "__main__":
    create_config_file()