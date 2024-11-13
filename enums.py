from enum import Enum, auto
import re

class RecipeSource(Enum):
    '''Enum of recipe sources'''
    UNKNOWN = auto()
    ALLRECIPES = auto()

    @classmethod
    def from_url(cls, url: str):
        if re.findall(r'allrecipes\.com/recipe/.*', url):
            return RecipeSource.ALLRECIPES
        return RecipeSource.UNKNOWN

class HTMLTag(Enum):
    '''Enum of relevant HTML tag types'''
    UNKNOWN = auto()
    OVERVIEW_LABEL = auto()
    OVERVIEW_TEXT = auto()
    INGREDIENT = auto()
    INGREDIENT_QUANTITY = auto()
    INGREDIENT_UNIT = auto()
    INGREDIENT_NAME = auto()
    STEP = auto()

    @classmethod
    def __from_allrecipes_tag(cls, tag: str, attrs: list[tuple[str, str | None]]):
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
                return HTMLTag.__from_allrecipes_tag(tag, attrs)
        return HTMLTag.UNKNOWN