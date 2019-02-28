
import json


class Manager:
    """Handles the configuration file.

      Example:
          # Retrieve configuration parameters.
          from config import Manager as ConfigManager
          config = ConfigManager.get_config()

    """

    filename = 'config.json'

    @staticmethod
    def get_config():
        """Returns the configuration parameters."""

        with open(Manager.filename, 'r') as f:
            config = f.read()
            return json.loads(config)
