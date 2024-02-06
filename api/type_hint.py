from enum import Enum

class GoodPage(str, Enum):
    NOPE = "NOPE"
    YES = "YES"
    MAYBE = "MAYBE"

    def __eq__(self, other: str | object) -> bool:
        if isinstance(other, str):
            return self.value == other.upper()
        elif isinstance(other, GoodPage):
            return self.value == other.value
        return super().__eq__(other)

    def __ne__(self, other: str | object) -> bool:
        if isinstance(other, str):
            return self.value != other.upper()
        elif isinstance(other, GoodPage):
            return self.value != other.value
        return super().__ne__(other)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"GoodPage.{self.value}"

    def __hash__(self) -> int:
        return hash(self.value)

    def __bool__(self) -> bool:
        return self == GoodPage.YES

    def __int__(self) -> int:
        match self:
            case GoodPage.NOPE:
                return 0
            case GoodPage.YES:
                return 1
            case GoodPage.MAYBE:
                return -1

    def __index__(self) -> int:
        return int(self)
