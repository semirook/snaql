import functools

def default():
    def inner(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return inner