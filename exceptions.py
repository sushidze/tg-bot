class ErrorMessage(Exception):
    """Send message to chat exception"""
    pass


class AnswerNot200(Exception):
    """URL request error"""
    pass


class Homeworksnotlist(Exception):
    """HW is not a list"""
    pass


class AnswerNotCorrect(Exception):
    """API response is not a dictionary."""
    pass


class StatusIsNotCorrect(Exception):
    """Unknown status value"""
    pass


class NotAllTokens(Exception):
    """Not all tokens defined"""
    pass


class AnswerNot200(Exception):
    """Исключение возникает из-за ошибки при запросе URL."""
    pass


class Homeworksnotlist(Exception):
    """Исключение возникает из-за того, что homeworks не список."""
    pass


class AnswerNotCorrect(Exception):
    """Исключение возникает из-за того, что ответ API не словарь."""
    pass


class StatusIsNotCorrect(Exception):
    """Исключение возникает из-за того, что значения status нет в утверждённых."""
    pass


class NotAllTokens(Exception):
    """Исключение возникает из-за того, что заданы не все токены."""
    pass
