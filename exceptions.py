class ErrorMessage(Exception):
    """Исключение возникает из-за ошибок при отправке сообщения в чат."""
    pass


class AnswerNot200(Exception):
    """Исключение возникает из-за ошибки при запросе URL."""
    pass


class Homeworksnotlist(Exception):
    """Исключение возникает из-за того, что homeworks не список."""
    pass


class AnswerNotDict(Exception):
    """Исключение возникает из-за того, что ответ API не словарь."""
    pass


class DictIsNotCorrect(Exception):
    """Исключение возникает из-за того, что в словаре нет поля homework_name."""
    pass


class StatusIsNotCorrect(Exception):
    """Исключение возникает из-за того, что в словаре нет поля homework_name."""
    pass


class NotAllTokens(Exception):
    """Исключение возникает из-за того, что заданы не все токены."""
    pass
