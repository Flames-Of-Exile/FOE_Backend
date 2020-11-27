import unittest

import tests.test_auth
import tests.test_campaigns
import tests.test_discord
import tests.test_guild
import tests.test_permissions
import tests.test_pins
import tests.test_socket
import tests.test_users
import tests.test_worlds


def main():
    suite = unittest.TestLoader().loadTestsFromModule(tests.test_auth)
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_campaigns))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_discord))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_guild))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_permissions))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_pins))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_socket))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_users))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_worlds))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
