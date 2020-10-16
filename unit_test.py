import unittest

import tests.test_auth
import tests.test_permissions
import tests.test_users


def main():
    suite = unittest.TestLoader().loadTestsFromModule(tests.test_users)
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_auth))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(tests.test_permissions))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
