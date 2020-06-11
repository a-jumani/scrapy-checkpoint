import logging
import os
import shutil


class CHECKPOINT_STATE(object):
    _RAND_NUM = '1247821013431315'
    IN_PROG = '_cp_ip' + _RAND_NUM
    OLD = '_cp_old' + _RAND_NUM
    CURRENT = '_cp' + _RAND_NUM


logger = logging.getLogger("checkpoint")


def create_checkpoint(path: str, empty: bool = False):
    """ Create copy of file(s) at path or an empty directory as a checkpoint.
    Atomic from the perspective of the caller.

    Args:
        path            path to a directory
        empty           if False, create copy of contents at path; otherwise
                        create empty checkpoint
    Preconditions:
        file(s) at path should not be changing while this function executes
    """
    logger.info('Creating checkpoint of {}'.format(path))

    if empty:
        # empty checkpoint
        os.mkdir(path + CHECKPOINT_STATE.IN_PROG)
    else:
        # copy contents
        shutil.copytree(path, path + CHECKPOINT_STATE.IN_PROG)
    logger.debug('Completed copying of contents at {}'.format(path))

    # rename current checkpoint to old checkpoint
    if os.path.isdir(path + CHECKPOINT_STATE.CURRENT):
        os.rename(path + CHECKPOINT_STATE.CURRENT, path + CHECKPOINT_STATE.OLD)
        logger.debug('Current checkpoint of {} renamed to old'.format(path))

    # rename copied contents to current checkpoint
    os.rename(path + CHECKPOINT_STATE.IN_PROG, path + CHECKPOINT_STATE.CURRENT)
    logger.debug('In progress checkpoint of {} renamed to current'.format(path))

    # remove old checkpoint
    _remove_directory(path + CHECKPOINT_STATE.OLD)

    logger.debug('Checkpoint of {} completed'.format(path))


def restore_checkpoint(path: str):
    """ Restore file(s) at path from a checkpoint, if available. Atomic and
    idempotent from the perspective of the caller.

    Args:
        path            path to a directory
    """
    logger.info('Restoring checkpoint of {}'.format(path))

    # current checkpoint exists
    if os.path.isdir(path + CHECKPOINT_STATE.CURRENT):
        shutil.rmtree(path)
        shutil.copytree(path + CHECKPOINT_STATE.CURRENT, path)
        logger.debug('Checkpoint for {} restored from current'.format(path))

    # old checkpoint exists - checkpoint creation failed after copying
    # contents successfully
    elif os.path.isdir(path + CHECKPOINT_STATE.OLD):
        os.rename(path + CHECKPOINT_STATE.IN_PROG,
                  path + CHECKPOINT_STATE.CURRENT)
        shutil.rmtree(path)
        shutil.copytree(path + CHECKPOINT_STATE.CURRENT, path)
        logger.debug('Checkpoint for {} restored from in-prog'.format(path))

    # no checkpoints
    else:
        _remove_directory(path)
        os.mkdir(path)
        logger.debug('No checkpoint found for {}'.format(path))

    # clean up - old and incomplete checkpoints
    _remove_directory(path + CHECKPOINT_STATE.OLD)
    _remove_directory(path + CHECKPOINT_STATE.IN_PROG)


def clear_checkpoint(path: str):
    """ Clear checkpoints of file(s) at path. Atomic and idempotent from the
    perspective of the caller.

    Args:
        path            path to a directory
    """
    logger.info('Clearing checkpoint of {}'.format(path))
    create_checkpoint(path, empty=True)
    os.rmdir(path + CHECKPOINT_STATE.CURRENT)


# helper functions
def _remove_directory(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        logging.debug('Deleted dir {}'.format(path))
