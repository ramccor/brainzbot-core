def listens_to_mentions(regex):
    """
    Decorator to add function and rule to routing table

    Returns Line that triggered the function.
    """

    def decorator(func):
        func.route_rule = ('mentions', regex)
        return func
    return decorator

def listens_to_all(regex):
    """
    Decorator to add function and rule to routing table

    Returns Line that triggered the function.
    """

    def decorator(func):
        func.route_rule = ('messages', regex)
        return func
    return decorator

def listens_to_command(cmd):
    """
    Decorator to listen for command with arguments return as list

    Returns Line that triggered the function
    as well as List of arguments not including the command.

    Can be used as a compability layer for simpler porting of plugins from other
    bots
    """

    def decorator(func):
        func.route_rule = ('commands', cmd)
        return func
    return decorator

def listens_to_regex_command(cmd, regex):
    """
    Decorator to listen for command with arguments checked by regex

    Returns Line that triggered the function.

    The best of both worlds
    """

    def decorator(func):
        func.route_rule = ('regex_commands', (cmd, regex))
        return func
    return decorator
