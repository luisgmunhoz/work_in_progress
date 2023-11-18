import logging
from functools import wraps
from typing import Any, Callable, Optional, Union


class MyLogger:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        return logging.getLogger(name)


def get_default_logger() -> logging.Logger:
    return MyLogger().get_logger()


TFunc = Callable[..., Any]


def log(
    _func: Optional[TFunc] = None,
    *,
    my_logger: Optional[Union[MyLogger, logging.Logger]] = None,
) -> TFunc:
    def decorator_log(func: TFunc) -> TFunc:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_default_logger()
            try:
                if my_logger is None:
                    first_args = next(
                        iter(args), None
                    )  # capture first arg to check for `self`
                    logger_params = [  # does kwargs have any logger
                        x
                        for x in kwargs.values()
                        if isinstance(x, logging.Logger) or isinstance(x, MyLogger)
                    ] + [  # # does args have any logger
                        x
                        for x in args
                        if isinstance(x, logging.Logger) or isinstance(x, MyLogger)
                    ]
                    if hasattr(first_args, "__dict__"):
                        logger_params = logger_params + [
                            x
                            for x in first_args.__dict__.values()
                            if isinstance(x, logging.Logger) or isinstance(x, MyLogger)
                        ]
                    h_logger = next(
                        iter(logger_params), MyLogger()
                    )  # get the next/first/default logger
                else:
                    h_logger = my_logger  # logger is passed explicitly to the decorator

                if isinstance(h_logger, MyLogger):
                    logger = h_logger.get_logger(func.__name__)
                else:
                    logger = h_logger

                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                logger.info(f"function {func.__name__} called with args {signature}")
            except Exception:
                pass

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(
                    f"Exception raised in {func.__name__}. exception: {str(e)}"
                )
                raise e

        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)
