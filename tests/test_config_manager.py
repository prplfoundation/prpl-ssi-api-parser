import unittest2

from prpl.config import Manager as ConfigManager


class TestConfigManager(unittest2.TestCase):
    """Tests the 'prpl.config.Manager' component."""

    def setUp(self):
        """Test environment setup."""

        pass

    def tearDown(self):
        """Test environment teardown."""

        pass

    def test__get_config(self):
        """Tests the TestConfig.get_config() method."""

        ConfigManager.filename = 'tests/dummy-config.json'
        dummy_config = ConfigManager.get_config()

        self.assertEqual('C:\\Program Files\\Graphviz\\bin', dummy_config['libs']['graphviz'])
