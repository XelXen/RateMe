# Description: This file contains the high-level schemas and functions

""" Libraries """

from enum import Enum
from msgspec import json
from typing import Dict, List
from database import Database
from functools import reduce
from config import ADJ_WEIGHT
import typing as t


""" Schema """


# Rating Types
class RatingType(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    def __call__(self) -> int:
        return self.value


# Entity Types
class EntityType(Enum):
    USER = "user"
    GROUP = "group"
    CHANNEL = "channel"

    def __call__(self) -> str:
        return self.value


# Feedback
class FeedbackSchema(t.TypedDict):
    rating: int
    comment: t.Optional[str]


# Entity
class EntitySchema(t.TypedDict):
    id: int
    entity_type: str
    rating: float
    feedbacks: Dict[int, FeedbackSchema]


# Config
class ConfigSchema(t.TypedDict):
    ban_llimit: t.Optional[float]
    mute_llimit: t.Optional[float]
    approved: List[int]


# Root
class RootSchema(t.TypedDict):
    entities: Dict[str, EntitySchema]
    configs: Dict[str, ConfigSchema]


""" Schema Functions """


# Get Root
def get_root(file_loc: str, load: bool = False) -> Database:
    """
    Get a database with the root schema.

    :param file_loc: File location to store the database
    :param load: Load the database from the file
    :return: Database object
    """
    if not load:
        root: RootSchema = {
            "entities": {},
            "configs": {},
        }
        with open(file_loc, "wb") as file:
            file.write(json.encode(root))

    return Database(file_loc, load=True)


# Get Entity
def get_entity(
    id: int,
    type: EntityType,
) -> EntitySchema:
    """
    Get an entity schema.

    :param id: ID of the entity
    :param entity_type: Type of the entity
    :return: Entity schema
    """
    return {
        "id": id,
        "entity_type": type(),
        "rating": 3,
        "feedbacks": {},
    }


# Get Config
def get_config() -> ConfigSchema:
    """
    Get a config schema.

    :return: Config schema
    """
    return {
        "ban_llimit": None,
        "mute_llimit": None,
        "approved": [],
    }


# Get Feedback
def get_feedback(
    rating: int,
    comment: t.Optional[str],
) -> FeedbackSchema:
    """
    Get a feedback schema.

    :param rating: Rating of the feedback
    :param comment: Comment of the feedback
    :return: Feedback schema
    """
    return {
        "rating": rating,
        "comment": comment,
    }


# Get EntityType
def get_entity_type(entity: str) -> t.Optional[EntityType]:
    """
    Get the entity type.

    :param entity: Entity type (user, group, channel)
    :return: Entity type
    """
    match entity:
        case "user":
            return EntityType.USER
        case "group":
            return EntityType.GROUP
        case "channel":
            return EntityType.CHANNEL
        case _:
            return None


# Get RatingType
def get_rating_type(rating: t.Union[str, int]) -> t.Optional[RatingType]:
    """
    Get the rating type.

    :param rating: Rating type (1, 2, 3, 4, 5)
    :return: Rating type
    """
    if isinstance(rating, str):
        rating = int(rating)

    match rating:
        case 1:
            return RatingType.ONE
        case 2:
            return RatingType.TWO
        case 3:
            return RatingType.THREE
        case 4:
            return RatingType.FOUR
        case 5:
            return RatingType.FIVE


""" Sugarcoated Functions """


# Get Rating
def get_rating(feedbacks: Dict[int, FeedbackSchema]) -> float:
    """
    Get the rating based on the user feedbacks.

    :param feedbacks: A dictionary of user feedbacks
    :param default_rating: Default rating for all users (prior belief), typically 3
    :param weight: Weight for how much the default rating influences the final result
    :return: Normalized rating
    """

    n_feedbacks = len(feedbacks)

    if n_feedbacks == 0:
        return 3

    mean_rating = (
        reduce(lambda x, y: x + y, [i for (i, _) in feedbacks.values()]) / n_feedbacks
    )

    # Bayesian adjusted rating
    return (ADJ_WEIGHT * 3 + n_feedbacks * mean_rating) / (ADJ_WEIGHT + n_feedbacks)


# Get Rating to Stars
def rating_to_stars(rating: float) -> str:
    """
    Get the star representation of the user's rating.

    :param rating: User's rating
    :return: Star representation
    """

    return "".join(["⭐" for _ in range(int(rating))])


# Get Rated Thumbnail
def get_thumb(rating: float) -> str:
    """
    Get the thumbnail based on the user's rating.

    :param rating: User's rating
    :return: URL of the thumbnail
    """

    if rating < 2:
        return "https://raw.githubusercontent.com/XelXen/RateMe/master/badges/L1.png"
    elif rating < 2.8:
        return "https://raw.githubusercontent.com/XelXen/RateMe/master/badges/L2.png"
    elif rating < 3.3:
        return "https://raw.githubusercontent.com/XelXen/RateMe/master/badges/L3.png"
    elif rating < 4:
        return "https://raw.githubusercontent.com/XelXen/RateMe/master/badges/L4.png"
    elif rating < 4.4:
        return "https://raw.githubusercontent.com/XelXen/RateMe/master/badges/L5.png"
    elif rating < 4.7:
        return "https://raw.githubusercontent.com/XelXen/RateMe/master/badges/R0.png"
    else:
        return "https://raw.githubusercontent.com/XelXen/RateMe/master/badges/R1.png"
