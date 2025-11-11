import json
import os


class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        default_config = {
            'language': 'en',
            'email_notifications': False,
            'email_address': '',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': '',
            'smtp_password': '',
            'enabled_error_types': [
                'SyntaxError',
                'TypeError',
                'ValueError',
                'AttributeError',
                'NameError',
                'ImportError',
                'IndexError',
                'KeyError',
                'FileNotFoundError',
                '404Error',
                '500Error',
                'DatabaseError',
                'ConnectionError'
            ],
            'log_retention_days': 30,
            'max_logs_per_file': 10000,
            'monitoring_interval': 2
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass

        return default_config

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_config(self):
        return self.config.copy()

    def update_config(self, updates):
        self.config.update(updates)
        return self.save_config()

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        return self.save_config()

    def reset_to_defaults(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.config = self.load_config()
        return self.save_config()