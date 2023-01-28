import os
from http import HTTPStatus

import requests
import telegram
import utils


class MockResponseGET:

    def __init__(self, url, params=None, random_timestamp=None,
                 current_timestamp=None, http_status=HTTPStatus.OK, **kwargs):
        assert (
            url.startswith(
                'https://practicum.yandex.ru/api/user_api/homework_statuses'
            )
        ), (
            'Check that you are doing request to correct API'
        )
        assert 'headers' in kwargs, (
            'Check that you sent all `headers` for request '
        )
        assert 'Authorization' in kwargs['headers'], (
            'Check that Authorization param was added to `headers`'
        )
        assert kwargs['headers']['Authorization'].startswith('OAuth '), (
            'Check Authorization in `headers` для begins with OAuth'
        )
        assert params is not None, (
            'Check that you sent `params`'
        )
        assert 'from_date' in params, (
            'Check that `from_date` was sent to `params`'
        )
        assert params['from_date'] == current_timestamp, (
            'Check that param `from_date` from `params` has timestamp'
        )
        self.random_timestamp = random_timestamp
        self.status_code = http_status

    def json(self):
        data = {
            "homeworks": [],
            "current_date": self.random_timestamp
        }
        return data


class MockTelegramBot:

    def __init__(self, token=None, random_timestamp=None, **kwargs):
        assert token is not None, (
            'Check that you sent a Telegram bot token'
        )
        self.random_timestamp = random_timestamp

    def send_message(self, chat_id=None, text=None, **kwargs):
        assert chat_id is not None, (
            'Check that you sent chat_id= '
        )
        assert text is not None, (
            'Check that you sent text= '
        )
        return self.random_timestamp


class TestHomework:
    HOMEWORK_STATUSES = {
        'approved': 'Great result. Approved!',
        'reviewing': 'On review.',
        'rejected': 'Review completed. Some changes are needed.'
    }
    ENV_VARS = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    for v in ENV_VARS:
        try:
            os.environ.pop(v)
        except KeyError:
            pass
    try:
        import homework
    except KeyError as e:
        for arg in e.args:
            if arg in ENV_VARS:
                assert False, (
                    'Make sure you have all env variables, '
                    'otherwise program will finish with `SystemExit`\n'
                    f'{repr(e)}'
                )
            else:
                raise
    except SystemExit:
        for v in ENV_VARS:
            os.environ[v] = ''

    def test_check_tokens_false(self):
        for v in self.ENV_VARS:
            try:
                os.environ.pop(v)
            except KeyError:
                pass

        import homework

        for v in self.ENV_VARS:
            utils.check_default_var_exists(homework, v)

        homework.PRACTICUM_TOKEN = None
        homework.TELEGRAM_TOKEN = None
        homework.TELEGRAM_CHAT_ID = None

        func_name = 'check_tokens'
        utils.check_function(homework, func_name, 0)
        tokens = homework.check_tokens()
        assert not tokens, (
            f'Check that function {func_name} returns False '
            'if some env variables are absent'
        )

    def test_check_tokens_true(self):
        for v in self.ENV_VARS:
            try:
                os.environ.pop(v)
            except KeyError:
                pass

        import homework

        for v in self.ENV_VARS:
            utils.check_default_var_exists(homework, v)

        homework.PRACTICUM_TOKEN = 'sometoken'
        homework.TELEGRAM_TOKEN = '1234:abcdefg'
        homework.TELEGRAM_CHAT_ID = 12345

        func_name = 'check_tokens'
        utils.check_function(homework, func_name, 0)
        tokens = homework.check_tokens()
        assert tokens, (
            f'Check that function {func_name} returns True if all variables are presented, '
        )

    def test_bot_init_not_global(self):
        import homework

        assert not (hasattr(homework, 'bot') and isinstance(getattr(homework, 'bot'), telegram.Bot)), (
            'Make sure that bot was initialized only in main()'
        )

    def test_logger(self, monkeypatch, random_timestamp):
        def mock_telegram_bot(*args, **kwargs):
            return MockTelegramBot(*args, random_timestamp=random_timestamp, **kwargs)

        monkeypatch.setattr(telegram, "Bot", mock_telegram_bot)

        import homework

        assert hasattr(homework, 'logging'), (
            'Make sure you set up logging'
        )

    def test_send_message(self, monkeypatch, random_timestamp):
        def mock_telegram_bot(*args, **kwargs):
            return MockTelegramBot(*args, random_timestamp=random_timestamp, **kwargs)

        monkeypatch.setattr(telegram, "Bot", mock_telegram_bot)

        import homework
        utils.check_function(homework, 'send_message', 2)

    def test_get_api_answers(self, monkeypatch, random_timestamp,
                             current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            return MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp, **kwargs
            )

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'get_api_answer'
        utils.check_function(homework, func_name, 1)

        result = homework.get_api_answer(current_timestamp)
        assert type(result) == dict, (
            f'Check that function `{func_name}` '
            'returns a dictionary'
        )
        keys_to_check = ['homeworks', 'current_date']
        for key in keys_to_check:
            assert key in result, (
                f'Check that function`{func_name}` '
                f'returns a dictionary with key `{key}`'
            )
        assert type(result['current_date']) == int, (
            f'Check that function `{func_name}` '
            'returns value of key `current_date` type `int` in API response '
        )
        assert result['current_date'] == random_timestamp, (
            f'Check that function `{func_name}` '
            'returns a correct value of key `current_date` in API response '
        )

    def test_get_500_api_answer(self, monkeypatch, random_timestamp,
                                current_timestamp, api_url):
        def mock_500_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                http_status=HTTPStatus.INTERNAL_SERVER_ERROR, **kwargs
            )

            def json_invalid():
                data = {
                }
                return data

            response.json = json_invalid
            return response

        monkeypatch.setattr(requests, 'get', mock_500_response_get)

        import homework

        func_name = 'get_api_answer'
        try:
            homework.get_api_answer(current_timestamp)
        except:
            pass
        else:
            assert False, (
                f'Make sure that function `{func_name}` checks API response not equal to 200 '
            )

    def test_parse_status(self, random_timestamp):
        test_data = {
            "id": 123,
            "status": "approved",
            "homework_name": str(random_timestamp),
            "reviewer_comment": "Good job!",
            "date_updated": "2020-02-13T14:40:57Z",
            "lesson_name": "Final project"
        }

        import homework

        func_name = 'parse_status'

        utils.check_function(homework, func_name, 1)

        result = homework.parse_status(test_data)
        assert result.startswith(
            f'Status has been changed "{random_timestamp}"'
        ), (
            'Check that project name was returned in '
            f'function `{func_name}`'
        )
        status = 'approved'
        assert result.endswith(self.HOMEWORK_STATUSES[status]), (
            'Check that verdict is correct for '
            f'`{status}` in function `{func_name}`'
        )

        test_data['status'] = status = 'rejected'
        result = homework.parse_status(test_data)
        assert result.startswith(
            f'Status has been changed "{random_timestamp}"'
        ), (
            'Check that project name was returned in parse_status() function'
        )
        assert result.endswith(
            self.HOMEWORK_STATUSES[status]
        ), (
            'Check that correct verdict was returned for '
            f'`{status}` in function parse_status()'
        )

    def test_check_response(self, monkeypatch, random_timestamp,
                            current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def valid_response_json():
                data = {
                    "homeworks": [
                        {
                            'homework_name': 'hw123',
                            'status': 'approved'
                        }
                    ],
                    "current_date": random_timestamp
                }
                return data

            response.json = valid_response_json
            return response

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'check_response'
        response = homework.get_api_answer(current_timestamp)
        status = homework.check_response(response)
        assert status, (
            f'Make sure function `{func_name} '
            'works correctly '
            'for correct API response'
        )

    def test_parse_status_unknown_status(self, monkeypatch, random_timestamp,
                                         current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def valid_response_json():
                data = {
                    "homeworks": [
                        {
                            'homework_name': 'hw123',
                            'status': 'unknown'
                        }
                    ],
                    "current_date": random_timestamp
                }
                return data

            response.json = valid_response_json
            return response

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'parse_status'
        response = homework.get_api_answer(current_timestamp)
        homeworks = homework.check_response(response)
        for hw in homeworks:
            status_message = None
            try:
                status_message = homework.parse_status(hw)
            except:
                pass
            else:
                assert False, (
                    f'Make sure that function `{func_name}` raises error '
                    'for unknown homework status in API response'
                )
            if status_message is not None:
                for hw_status in self.HOMEWORK_STATUSES:
                    assert not status_message.endswith(hw_status), (
                        f'Make sure that function `{func_name} does not return correct '
                        'answer for unknown homework status'
                    )

    def test_parse_status_no_status_key(self, monkeypatch, random_timestamp,
                                        current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def valid_response_json():
                data = {
                    "homeworks": [
                        {
                            'homework_name': 'hw123',
                        }
                    ],
                    "current_date": random_timestamp
                }
                return data

            response.json = valid_response_json
            return response

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'parse_status'
        response = homework.get_api_answer(current_timestamp)
        homeworks = homework.check_response(response)
        for hw in homeworks:
            status_message = None
            try:
                status_message = homework.parse_status(hw)
            except:
                pass
            else:
                assert False, (
                    f'Make sure that function `{func_name}` raises error '
                    'if `homework_status` is absent in API response'
                )
            if status_message is not None:
                for hw_status in self.HOMEWORK_STATUSES:
                    assert not status_message.endswith(hw_status), (
                        f'Make sure that function `{func_name} does not return '
                        'correct reply without `homework_status` key'
                    )

    def test_parse_status_no_homework_name_key(self, monkeypatch, random_timestamp,
                                               current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def valid_response_json():
                data = {
                    "homeworks": [
                        {
                            'status': 'unknown'
                        }
                    ],
                    "current_date": random_timestamp
                }
                return data

            response.json = valid_response_json
            return response

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'parse_status'
        response = homework.get_api_answer(current_timestamp)
        homeworks = homework.check_response(response)
        try:
            for hw in homeworks:
                homework.parse_status(hw)
        except KeyError:
            pass
        else:
            assert False, (
                f'Make sure that function `{func_name}` do work correctly '
                'if `homework_name` key is absent in API response'
            )

    def test_check_response_no_homeworks(self, monkeypatch, random_timestamp,
                                         current_timestamp, api_url):
        def mock_no_homeworks_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def json_invalid():
                data = {
                    "current_date": random_timestamp
                }
                return data

            response.json = json_invalid
            return response

        monkeypatch.setattr(requests, 'get', mock_no_homeworks_response_get)

        import homework

        func_name = 'check_response'
        result = homework.get_api_answer(current_timestamp)
        try:
            homework.check_response(result)
        except:
            pass
        else:
            assert False, (
                f'Make sure that function `{func_name} '
                'checks that API response does not have '
                '`homeworks` key and raises error'
            )

    def test_check_response_not_dict(self, monkeypatch, random_timestamp,
                                     current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def valid_response_json():
                data = [{
                    "homeworks": [
                        {
                            'homework_name': 'hw123',
                            'status': 'approved'
                        }
                    ],
                    "current_date": random_timestamp
                }]
                return data

            response.json = valid_response_json
            return response

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'check_response'
        response = homework.get_api_answer(current_timestamp)
        try:
            status = homework.check_response(response)
        except TypeError:
            pass
        else:
            assert status, (
                f'Make sure that function `{func_name} '
                'checks API response incorrect type'
            )

    def test_check_response_homeworks_not_in_list(self, monkeypatch, random_timestamp,
                                                  current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def valid_response_json():
                data = {
                    "homeworks":
                        {
                            'homework_name': 'hw123',
                            'status': 'approved'
                        },
                    "current_date": random_timestamp
                }
                return data

            response.json = valid_response_json
            return response

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'check_response'
        response = homework.get_api_answer(current_timestamp)
        try:
            homeworks = homework.check_response(response)
        except:
            pass
        else:
            assert not homeworks, (
                f'Make sure that function `{func_name} '
                'checks `homeworks` key is not a list in API response'
            )

    def test_check_response_empty(self, monkeypatch, random_timestamp,
                                  current_timestamp, api_url):
        def mock_empty_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                **kwargs
            )

            def json_invalid():
                data = {
                }
                return data

            response.json = json_invalid
            return response

        monkeypatch.setattr(requests, 'get', mock_empty_response_get)

        import homework

        func_name = 'check_response'
        result = homework.get_api_answer(current_timestamp)
        try:
            homework.check_response(result)
        except:
            pass
        else:
            assert False, (
                f'Make sure that function `{func_name} '
                'checks API response has empty dictionary and raises an error'
            )

    def test_api_response_timeout(self, monkeypatch, random_timestamp,
                                  current_timestamp, api_url):
        def mock_response_get(*args, **kwargs):
            response = MockResponseGET(
                *args, random_timestamp=random_timestamp,
                current_timestamp=current_timestamp,
                http_status=HTTPStatus.REQUEST_TIMEOUT, **kwargs
            )
            return response

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import homework

        func_name = 'check_response'
        try:
            homework.get_api_answer(current_timestamp)
        except:
            pass
        else:
            assert False, (
                f'Make sure that function `{func_name}` checks API response not equal to 200'
            )
