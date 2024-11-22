'''Utility enums and functions for recipe parsing and display.'''

import re
import spacy
import unicodedata

from enum import Enum, auto
from fractions import Fraction
from nltk.corpus import wordnet as wn

#############
# VARIABLES #
#############

nlp = spacy.load("en_core_web_md")

#########
# ENUMS #
#########

class RecipeSource(Enum):
    '''Enum of recipe sources'''
    UNKNOWN = auto()
    ALLRECIPES = auto()
    SERIOUSEATS = auto()
    EPICURIOUS = auto()

    @classmethod
    def from_url(cls, url: str):
        if re.findall(r'allrecipes\.com/recipe/.*', url):
            return RecipeSource.ALLRECIPES
        elif re.findall(r'seriouseats\.com/.*recipe', url):
            return RecipeSource.SERIOUSEATS
        elif re.findall(r'epicurious\.com/recipes/.*', url):
            return RecipeSource.EPICURIOUS
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
    def __from_seriouseats_tag(cls, tag: str,
                               attrs: list[tuple[str, str | None]]):
        if tag == 'h1':
            if attrs == [('class', 'heading__title')]:
                return HTMLTag.TITLE
        elif tag == 'span':
            if attrs == [('class', 'meta-text__label')]:
                return HTMLTag.OVERVIEW_LABEL
            elif attrs == [('class', 'meta-text__data')]:
                return HTMLTag.OVERVIEW_TEXT
            elif attrs == [('data-ingredient-quantity', 'true')]:
                return HTMLTag.INGREDIENT_QUANTITY
            elif attrs == [('data-ingredient-unit', 'true')]:
                return HTMLTag.INGREDIENT_UNIT
            elif attrs == [('data-ingredient-name', 'true')]:
                return HTMLTag.INGREDIENT_NAME
        elif tag == 'section':
            if ('class', 'comp section--ingredients section') in attrs:
                return HTMLTag.INGREDIENTS_LIST
            elif ('class', 'comp section--instructions section') \
                    in attrs:
                return HTMLTag.STEPS_LIST
        elif tag == 'li':
            if ('class', 'structured-ingredients__list-item') in attrs:
                return HTMLTag.INGREDIENT
        elif tag == 'p':
            if ('class', 'comp mntl-sc-block mntl-sc-block-html') in attrs:
                return HTMLTag.STEP
        return HTMLTag.UNKNOWN
    
    @classmethod
    def __from_epicurious_tag(cls, tag: str,
                              attrs: list[tuple[str, str | None]]):
        if tag == 'h1':
            if ('data-testid', 'ContentHeaderHed') in attrs:
                return HTMLTag.TITLE
        elif tag == 'p':
            if attrs == [('class', 'BaseWrap-sc-gjQpdd BaseText-ewhhUZ'
                          ' InfoSliceKey-gHIvng iUEiRd dWUQxN hykkRA')]:
                return HTMLTag.OVERVIEW_LABEL
            elif attrs == [('class', 'BaseWrap-sc-gjQpdd BaseText-ewhhUZ'
                            ' InfoSliceValue-tfmqg iUEiRd bbekcU fkSlPp')]:
                return HTMLTag.OVERVIEW_TEXT
            else:
                return HTMLTag.STEP
        elif tag == 'div':
            if ('data-testid', 'IngredientList') in attrs:
                return HTMLTag.INGREDIENTS_LIST
            elif attrs == [('class', 'BaseWrap-sc-gjQpdd BaseText-ewhhUZ'
                            ' Description-cSrMCf iUEiRd bGCtOd fsKnGI')]:
                return HTMLTag.INGREDIENT_NAME
            elif ('data-testid', 'InstructionsWrapper') in attrs:
                return HTMLTag.STEPS_LIST
        return HTMLTag.UNKNOWN

    @classmethod
    def from_tag(cls, source: RecipeSource, tag: str,
                 attrs: list[tuple[str, str | None]]):
        match source:
            case RecipeSource.ALLRECIPES:
                return HTMLTag.__from_allrecipes_tag(tag, attrs)
            case RecipeSource.SERIOUSEATS:
                return HTMLTag.__from_seriouseats_tag(tag, attrs)
            case RecipeSource.EPICURIOUS:
                return HTMLTag.__from_epicurious_tag(tag, attrs)
        return HTMLTag.UNKNOWN

class NounType(Enum):
    '''Enum of relevant noun types'''
    UNKNOWN = auto()
    FOOD = auto()
    MEASURE = auto()
    TEMPERATURE = auto()
    TOOL = auto()

    @classmethod
    def from_str(cls, noun: str):
        ntypes = []
        sets = wn.synsets(noun, wn.NOUN)
        for s in sets:
            for ss in s.hypernym_paths():
                if (wn.synset('kitchen_utensil.n.01') in ss or \
                    wn.synset('kitchen_appliance.n.01') in ss or \
                    wn.synset('container.n.01') in ss) and \
                        NounType.TOOL not in ntypes:
                    ntypes.append(NounType.TOOL)
                elif wn.synset('measure.n.02') in ss and \
                NounType.MEASURE not in ntypes:
                    ntypes.append(NounType.MEASURE)
                elif (wn.synset('food.n.01') in ss or \
                      wn.synset('food.n.02') in ss or \
                      wn.synset('leaven.n.01') in ss) and \
                        NounType.FOOD not in ntypes:
                    ntypes.append(NounType.FOOD)
                elif (wn.synset('temperature.n.01') in ss or \
                      wn.synset('fire.n.03') in ss or \
                      wn.synset('temperature_unit.n.01') in ss) and \
                      NounType.TEMPERATURE not in ntypes:
                    ntypes.append(NounType.TEMPERATURE)
        return ntypes

#############
# FUNCTIONS #
#############

def str_to_fraction(data: str):
    sum = Fraction()
    table = str.maketrans({u'⁄': '/'})
    data = unicodedata.normalize('NFKD', data).translate(table).split()
    for val in data:
        try:
            sum += Fraction(val)
        except:
            continue
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
