import asyncio
import os

import logging
logger = logging.getLogger(__name__)


async def cancel_futures(*futures):
    '''
    Cancel each future in ``futures``.

    This handles cancellation for Task vs Future correctly and does not raise
    CancelledError to its caller.
    '''
    gather = asyncio.gather(*futures)
    gather.cancel()

    try:
        await gather
    except asyncio.CancelledError:
        pass


def get_path(relative_path=None):
    """ Return an absolute path to a project relative path. """

    root_path = os.path.dirname(os.path.dirname(__file__))

    if relative_path is None:
        return root_path
    else:
        return os.path.abspath(os.path.join(root_path, relative_path))


def raise_future_exception(future):
    '''
    If a future has no return value, then you probably won't call its
    ``result()``, but you still want to detect any exceptions that occur.

    This silently swallows CancelledError, but any other exception is raised.
    '''

    def raise_exception(f):
        try:
            f.result()
        except asyncio.CancelledError:
            pass

    future.add_done_callback(raise_exception)


async def wait_first(*futures):
    '''
    Wait for one future in ``futures`` to finish, then cancel the rest.

    Returns the future that finished first.
    '''
    done, pending = await asyncio.wait(
        futures,
        return_when=asyncio.FIRST_COMPLETED
    )

    await cancel_futures(*pending)
    return done.pop()
