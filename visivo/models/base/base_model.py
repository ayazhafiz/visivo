from pydantic import StringConstraints, Discriminator, Tag, BaseModel, ConfigDict
from typing_extensions import Annotated
from typing import Any, Union, NewType
import re

REF_REGEX = r"^ref\(\s*(?P<ref_name>[a-zA-Z0-9\s'\"\-_]+)\)$"
STATEMENT_REGEX = r"^\s*query\(\s*(?P<query_statement>.+)\)\s*$|^\s*column\(\s*(?P<column_name>.+)\)\s*$"
INDEXED_STATEMENT_REGEX = r"^\s*column\(\s*(?P<column_name>.+)\)\[[0-9]+\]\s*$"

RefString = NewType(
    "RefString",
    Annotated[Annotated[str, StringConstraints(pattern=REF_REGEX)], Tag("Ref")],
)


def generate_ref_field(class_to_discriminate):
    return NewType(
        class_to_discriminate.__name__,
        Annotated[
            Union[
                RefString,
                Annotated[class_to_discriminate, Tag(class_to_discriminate.__name__)],
            ],
            Discriminator(ModelStrDiscriminator(class_to_discriminate)),
        ],
    )


class ModelStrDiscriminator:
    def __init__(self, class_to_discriminate):
        self.class_name = class_to_discriminate.__name__

    def __name__(self):
        return self.class_name

    def __call__(self, value):
        if isinstance(value, str):
            return "Ref"
        if isinstance(value, (dict, BaseModel)):
            return self.class_name
        else:
            return None


class BaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def id(self):
        return (
            self.__class__.__name__
            + " - "
            + str(hash((type(self),) + tuple(self.__dict__.values())))
        )

    @classmethod
    def is_obj(cls, obj) -> bool:
        return not cls.is_ref(obj)

    @classmethod
    def is_ref(cls, obj) -> bool:
        return isinstance(obj, str) and re.search(REF_REGEX, obj)

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return self.id()
