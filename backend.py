# Description: This file contains the high-level schemas and functions

""" Libraries """

from enum import Enum
from msgspec import Struct, json
from typing import Tuple, Dict, List
from database import Database
from functools import reduce

""" Schema """


# Rating Types
class Rating(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


# User Object
class User(Struct):
    uid: int
    rating: float | None = None
    feedbacks: Dict[int, Tuple[int, str]] = {}


# Community Object
class Community(Struct):
    cid: int
    ban_llimit: float | None = None
    mute_llimit: float | None = None


# Root Schema
class Root(Struct):
    users: Dict[int, User] = {}
    communities: List[Community] = []


""" Functions """


# Get Root
def get_root(file_loc: str, load: bool = False) -> Database:
    """ Get a database with root schema. """
    if not load:
        root = Root()
        with open(file_loc, "wb") as file:
            file.write(json.encode(root))

    return Database(file_loc, load=True)


# Get Rating
def get_rating(feedbacks: Dict[int, Tuple[int, str]]) -> float:
    """ Get the average rating from the feedbacks. """
    return reduce(lambda x, y: x + y, [i for (i, _) in feedbacks.values()]) / len(feedbacks)
