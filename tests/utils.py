from inspect import signature
from types import ModuleType


def check_function(scope: ModuleType, func_name: str, params_qty: int = 0):
    """Checks if scope has a function with specific name and params with qty"""
    assert hasattr(scope, func_name), (
        f'No function `{func_name}`. '
        'Do not remove and rename it'
    )

    func = getattr(scope, func_name)

    assert callable(func), (
        f'`{func_name}` should be a function'
    )

    sig = signature(func)
    assert len(sig.parameters) == params_qty, (
        f'Function `{func_name}` should get '
        f'number of arguments = {params_qty}'
    )


def check_default_var_exists(scope: ModuleType, var_name: str) -> None:
    """
    Checks if precode variable exists in scope with a proper type.
    :param scope: Module to look for a variable
    :param var_name: Variable you want to check
    :return: None. It's an assert
    """
    assert hasattr(scope, var_name), (
        f'No variable `{var_name}` found. Do not remove and rename it'
    )
    var = getattr(scope, var_name)
    assert not callable(var), (
        f'{var_name} should be variable not a function'
    )

