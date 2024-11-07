from enum import Enum, auto

# Enum of recipe sources
class RecipeSource(Enum):
    UNKNOWN = auto()
    ALLRECIPES = auto()

# Enum of relevant HTML tag types
class HTMLTag(Enum):
    UNKNOWN = auto()
    OVERVIEW_LABEL = auto()
    OVERVIEW_TEXT = auto()
    INGREDIENT = auto()
    INGREDIENT_QUANTITY = auto()
    INGREDIENT_UNIT = auto()
    INGREDIENT_NAME = auto()
    STEP = auto()

    @classmethod
    def from_allrecipes_tag(cls, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == 'div':
            if attrs == [('class', 'mm-recipes-details__label')]:
                return HTMLTag.OVERVIEW_LABEL
            elif attrs == [('class', 'mm-recipes-details__value')]:
                return HTMLTag.OVERVIEW_TEXT
        elif tag == 'li':
            if ('class', 'mm-recipes-structured-ingredients__list-item ') in attrs:
                return HTMLTag.INGREDIENT
        elif tag == 'span':
            if attrs == [('data-ingredient-quantity', 'true')]:
                return HTMLTag.INGREDIENT_QUANTITY
            elif attrs == [('data-ingredient-unit', 'true')]:
                return HTMLTag.INGREDIENT_UNIT
            elif attrs == [('data-ingredient-name', 'true')]:
                return HTMLTag.INGREDIENT_NAME
        elif tag == 'p':
            if ('class', 'comp mntl-sc-block mntl-sc-block-html') in attrs:
                return HTMLTag.STEP
        return HTMLTag.UNKNOWN

    @classmethod
    def from_tag(cls, source: RecipeSource, tag: str, attrs: list[tuple[str, str | None]]):
        match source:
            case RecipeSource.ALLRECIPES:
                return cls.from_allrecipes_tag(tag, attrs)
        return HTMLTag.UNKNOWN