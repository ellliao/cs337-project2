'''Recipe data representations.'''

from fractions import Fraction

class Ingredient:
    '''Struct holding ingredient information'''

    def __init__(self, name: str | None = None,
                 quantity: Fraction | None = None,
                 unit: str | None = None):
        self.name = name
        '''Name of the ingredient, e.g. salt'''
        self.quantity = quantity
        '''Quantity of the ingredient, e.g. 1/2'''
        self.unit = unit
        '''Unit of the ingredient, e.g. tsp'''

class IntermediateIngredient:
    '''Struct holding intermediate ingredient information, e.g. dough'''

    def __init__(self, ingredients: list[Ingredient]):
        self.name: str | None = None
        '''Name of the intermediate ingredient, if assigned, e.g. dough'''
        self.ingredients = ingredients
        '''Original ingredients involved, e.g. [flour, eggs]'''

class IngredientState:
    '''Struct holding the current state of ingredients at a given step'''

    def __init__(self, remaining: list[Ingredient],
                 intermediate: list[IntermediateIngredient] = [],
                 focus: int = -1):
        self.remaining: list[Ingredient] = remaining.copy()
        '''Remaining unused ingredients'''
        self.intermediate: list[IntermediateIngredient] = intermediate.copy()
        '''Any intermediate collections of ingredients'''
        self.focus = focus
        '''Index of currently referenced intermediate ingredient'''

class Step:
    '''Struct holding step information'''

    def __init__(self, text: str, init_state: IngredientState):
        self.text: str = text
        '''Text associated with the step'''
        self.ingredients: list[Ingredient] = []
        '''List of ingredients used in this step'''
        self.state: IngredientState = init_state
        '''State of the ingredients at this step'''
        self.tools: list[str] = []
        '''Tools mentioned in this step'''
        self.methods: list[str] = []
        '''Methods mentioned in this step'''
        self.times: list[str] = []
        '''Times mentioned in this step'''
        self.temps: list[str] = []
        '''Temperatures / measures of "doneness" mentioned in this step'''
    
class Recipe:
    '''Struct holding recipe information'''

    def __init__(self):
        self.title: str = ""
        '''Title of the recipe'''
        self.ingredients: list[Ingredient] = []
        '''List of ingredients used in the recipe'''
        self.tools: list[str] = []
        '''List of tools used in the recipe'''
        self.steps: list[Step] = []
        '''List of recipe steps'''
        self.other: dict[str, str] = {}
        '''Other miscellaneous recipe information'''
