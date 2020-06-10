import logging

logger = logging.getLogger("checkpoint")


def create_checkpoint(path: str):
    """ Create copy of file(s) at path as a checkpoint. Atomic from the
    perspective of the caller.

    Args:
        path            path to a directory
    Preconditions:
        file(s) at path should not be changing while this function executes
    """
    pass


def restore_checkpoint(path: str):
    """ Restore file(s) at path from a checkpoint, if available. Atomic and
    idempotent from the perspective of the caller.

    Args:
        path            path to a directory
    """
    pass


def clear_checkpoint(path: str):
    """ Clear checkpoints of file(s) at path. Atomic and idempotent from the
    perspective of the caller.

    Args:
        path            path to a directory
    """
    pass
