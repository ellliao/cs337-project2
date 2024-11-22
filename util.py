'''Utility enums and functions for recipe parsing and display.'''

import re
import unicodedata

from enum import Enum, auto
from fractions import Fraction
from nltk.corpus import wordnet as wn

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
    TITLE = auto()
    OVERVIEW_LABEL = auto()
    OVERVIEW_TEXT = auto()
    INGREDIENTS_LIST = auto()
    INGREDIENT = auto()
    INGREDIENT_QUANTITY = auto()
    INGREDIENT_UNIT = auto()
    INGREDIENT_NAME = auto()
    STEPS_LIST = auto()
    STEP = auto()

    @classmethod
    def __from_allrecipes_tag(cls, tag: str,
                              attrs: list[tuple[str, str | None]]):
        if tag == 'h1':
            if attrs == [('class', 'article-heading text-headline-400')]:
                return HTMLTag.TITLE
        elif tag == 'div':
            if attrs == [('class', 'mm-recipes-details__label')]:
                return HTMLTag.OVERVIEW_LABEL
            elif attrs == [('class', 'mm-recipes-details__value')]:
                return HTMLTag.OVERVIEW_TEXT
            elif ('class', 'comp mm-recipes-steps mntl-block') \
                    in attrs:
                return HTMLTag.STEPS_LIST
        elif tag == 'ul':
            if ('class', 'mm-recipes-structured-ingredients__list') in attrs:
                return HTMLTag.INGREDIENTS_LIST
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
    def from_tag(cls, source: RecipeSource, tag: str,
                 attrs: list[tuple[str, str | None]]):
        match source:
            case RecipeSource.ALLRECIPES:
                return HTMLTag.__from_allrecipes_tag(tag, attrs)
        return HTMLTag.UNKNOWN

class NounType(Enum):
    '''Enum of relevant noun types'''
    UNKNOWN = auto()
    TOOL = auto()

    @classmethod
    def from_str(cls, noun: str):
        sets = wn.synsets(noun, wn.NOUN)
        for s in sets:
            for ss in s.hypernym_paths():
                if wn.synset('kitchen_utensil.n.01') in ss or \
                    wn.synset('kitchen_appliance.n.01') in ss or \
                    wn.synset('container.n.01') in ss:
                    return NounType.TOOL
        return NounType.UNKNOWN

def str_to_fraction(data: str):
    sum = Fraction()
    table = str.maketrans({u'⁄': '/'})
    data = unicodedata.normalize('NFKD', data).translate(table).split()
    for val in data:
        sum += Fraction(val)
    return sum

def fraction_to_str(frac: Fraction):
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator >= frac.denominator:
        return ' '.join([str(frac.numerator // frac.denominator),
                         str(Fraction(frac.numerator % frac.denominator,
                                      frac.denominator))])
    else:
        return str(frac)
