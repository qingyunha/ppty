import sys
import logging

__all__ = ('logger')

logger = logging.getLogger(__package__)
logger.addHandler(logging.StreamHandler(stream=sys.stderr)) # stderr
