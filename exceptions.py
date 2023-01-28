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
