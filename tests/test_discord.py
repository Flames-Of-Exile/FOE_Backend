from .setup import BasicTests
from discord_token import confirm_token, generate_confirmation_token


class DiscordTests(BasicTests):

    def test_generate_token_generates_string(self):
        username = "test"
        token = generate_confirmation_token(username)
        self.assertEqual(type(token), str)
        self.assertNotEqual(token, username)

    def test_confirm_token_success(self):
        username = "test"
        token = generate_confirmation_token(username)
        result = confirm_token(token)
        self.assertEqual(result, username)

    def test_confirm_token_fail_incorrect_username(self):
        username = "test"
        token = generate_confirmation_token("not_test")
        result = confirm_token(token)
        self.assertNotEqual(username, result)

    def test_confirm_token_fail_expiration(self):
        username = "test"
        token = generate_confirmation_token(username)
        result = confirm_token(token, -1)
        self.assertFalse(result)
