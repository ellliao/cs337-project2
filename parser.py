'''Recipe parsing and extraction classes and functions.'''

import re
import recipe as r
import requests
import util as u

from html.parser import HTMLParser

####################
# HELPER FUNCTIONS #
####################

def find_ingredient(name: str, ingredients: list[r.Ingredient]) -> list[int]:
    '''Finds the list of indices of the ingredients possibly being referenced'''

    ingr_inds = []
    components = name.split()

    # Remove any determiners
    if components[0] in ['the', 'a', 'an']:
        del components[0]
        name = ' '.join(components)

    # If name is empty, return
    if not name:
        return ingr_inds
    
    # Initialize confidence to 1/2 of number of words
    max_confidence = len(components) / 2

    for i in range(len(ingredients)):
        if name == ingredients[i].name:
            # Return if an exact match
            return [i]
        elif name in ingredients[i].name:
            # If a substring, add to list and limit search to other substrs
            ingr_inds.append(i)
            max_confidence = len(components) + 1
        elif max_confidence <= len(components):
            # Check how many words match and add to list if == current max or
            # reset list to just it + update max if >
            confidence = 0
            for wd in components:
                if wd in ingredients[i].name:
                    confidence += 1
            if confidence > max_confidence:
                ingr_inds = [i]
            elif confidence == max_confidence:
                ingr_inds.append(i)
    
    return ingr_inds

def parse_nouns(step: r.Step, doc) -> None:
    '''Extract ingredients, tools, and temps from a SpaCy parse'''

    from_prev = ''
    for chunk in doc.noun_chunks:

        # If the root verb is mistakenly in the chunk, remove it.
        name = chunk.text
        if chunk.root.dep_ == 'ROOT' and step.methods[0] in name:
            name = name.partition(step.methods[0])[2]
            if not name:
                continue
            name = name[1:-1]
        if from_prev:
            name = ' '.join([from_prev, name])
            from_prev = ''
        
        # If the noun chunk is not a dobj, pobj, or conj, ignore it.
        if chunk.root.dep_ not in ['dobj', 'pobj', 'conj', 'ROOT', 'appos']:
            continue
        
        # Check the type of noun
        ntypes = u.NounType.from_str(chunk.root.text)
        if u.NounType.MEASURE in ntypes and \
            doc[chunk.start].ent_type_ == 'CARDINAL':
            from_prev = chunk.text
            continue
        if u.NounType.TOOL in ntypes:
            step.tools.append(chunk.text)
        elif u.NounType.TEMPERATURE in ntypes or \
            (chunk.end-chunk.start > 2 and doc[chunk.end-2].text == 'degrees'):
            step.temps.append(chunk.text.strip('().:,'))
        else:
            # Check if the referenced noun is an ingredient.
            ref_ingr = r.Ingredient.from_str(name)
            if ref_ingr.name:
                ingr_inds = find_ingredient(ref_ingr.name, step.state.remaining)
                # Assume ambiguous ingredient means inclusive
                offset = 0
                for i in ingr_inds:
                    ingr = r.Ingredient(
                        ref_ingr.name if len(ingr_inds) == 1 \
                            else step.state.remaining[i-offset].name,
                        ref_ingr.quantity if ref_ingr.quantity \
                            else step.state.remaining[i-offset].quantity,
                        ref_ingr.unit if ref_ingr.unit \
                            else step.state.remaining[i-offset].unit)
                    if ingr.quantity and \
                        step.state.remaining[i-offset].quantity \
                            <= ingr.quantity:
                        del step.state.remaining[i-offset]
                        offset += 1
                    elif ingr.quantity:
                        step.state.remaining[i-offset].quantity \
                            -= ingr.quantity
                    step.ingredients.append(ingr)

def parse_and_add_step(instr: str, recipe: r.Recipe) -> None:
    '''Parses an instruction into maybe more steps and adds to recipe.'''

    # Split recipe instruction into "sentences" for SpaCy parser
    steps = re.split(r'(?:\.|;|, then)\s+', instr)

    for text in steps:

        # Skip if empty
        if not text:
            continue

        # Form a nice sentence for the step text, and initialize step
        text = ''.join([text[0].upper(), text[1:len(text)]])
        if not text.endswith('.'):
            text = ''.join([text, '.'])
        if len(recipe.steps) > 0:
            step: r.Step = r.Step(text, recipe.steps[-1].state)
        else:
            step: r.Step = r.Step(text, r.IngredientState(recipe.ingredients))

        # Uncapitalize the first letter. This prevents SpaCy from reading the
        # first word as a proper noun (imperative sentences are less common in
        # its dataset).
        text = ''.join([text[0].lower(), text[1:len(text)]])

        # Based on the dependency + part of speech tagging, extract necessary
        # information.
        doc = u.nlp(text)
        for (i, token) in enumerate(doc):

            # If the parser interpreted an imperative sentence as an NP,
            # correct it.
            if token.dep_ == 'ROOT' and token.head.pos_ == 'NOUN':
                for j in range(i,-1,-1):
                    if j == 0 or \
                        (j > 0 and doc[j-1].dep_ == 'punct'):
                        doc[j].dep_ = 'ROOT'
                        token.dep_ = 'dobj'
                        step.methods.append(doc[j].text)
                        break

            # Extract methods
            if token.dep_ == 'ROOT':
                step.methods.append(token.text)
            elif token.dep_ == 'conj':
                if token.head.text in step.methods:
                    step.methods.append(token.text)

        # Extract ingredients, tools, and temps
        parse_nouns(step, doc)

        # Extract times
        for ent in doc.ents:
            if ent.label_ == 'TIME' or ent.label_ == 'DATE':
                step.times.append(ent.text)

        # Save step to recipe
        recipe.steps.append(step)

################
# PARSER CLASS #
################

class RecipeHTMLParser(HTMLParser):
    '''HTML parser that handles recipes'''

    def __init__(self, source: u.RecipeSource, convert_charrefs: bool = True) -> None:
        # Initialize class, setting recipe to empty
        self.source = source
        self.recipe = r.Recipe()
        self.current_tag = u.HTMLTag.UNKNOWN
        self.current_section = u.HTMLTag.UNKNOWN
        super().__init__(convert_charrefs=convert_charrefs)
    
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Save the current tag
        self.current_tag = u.HTMLTag.from_tag(self.source, tag, attrs)
        match self.current_tag:
            case u.HTMLTag.INGREDIENTS_LIST:
                self.current_section = u.HTMLTag.INGREDIENTS_LIST
            case u.HTMLTag.INGREDIENT:
                if self.current_section == u.HTMLTag.INGREDIENTS_LIST:
                    self.ingredient = r.Ingredient()
            case u.HTMLTag.STEPS_LIST:
                self.current_section = u.HTMLTag.STEPS_LIST
        return super().handle_starttag(tag, attrs)
    
    def handle_data(self, data: str) -> None:
        # Handle text between tags as appropriate
        match self.current_tag:
            case u.HTMLTag.TITLE:
                self.recipe.title = data.strip()
            case u.HTMLTag.OVERVIEW_LABEL:
                self.label = data.lower().strip(':,.! \n\t')
            case u.HTMLTag.OVERVIEW_TEXT:
                self.recipe.other[self.label] = data.strip()
            case u.HTMLTag.INGREDIENT_QUANTITY:
                if self.current_section == u.HTMLTag.INGREDIENTS_LIST:
                    self.ingredient.quantity = u.str_to_fraction(data.strip())
            case u.HTMLTag.INGREDIENT_UNIT:
                if self.current_section == u.HTMLTag.INGREDIENTS_LIST:
                    self.ingredient.unit = data.strip()
            case u.HTMLTag.INGREDIENT_NAME:
                if self.current_section == u.HTMLTag.INGREDIENTS_LIST:
                    self.ingredient.name = data.strip()
                    self.recipe.ingredients.append(self.ingredient)
            case u.HTMLTag.STEP:
                if self.current_section == u.HTMLTag.STEPS_LIST:
                    parse_and_add_step(data.strip(), self.recipe)
        return super().handle_data(data)

    def handle_endtag(self, tag: str) -> None:
        # Reset tag
        self.current_tag = u.HTMLTag.UNKNOWN
        return super().handle_endtag(tag)

################
# API FUNCTION #
################

def get_recipe_from_url(url: str) -> r.Recipe | None:
    '''Retrieves the text of a recipe from a given URL'''

    # Find recipe source; return None if unsupported
    source = u.RecipeSource.from_url(url)
    if source == u.RecipeSource.UNKNOWN:
        return None

    # Add appropriate HTTPS tag if not there
    if not re.match(r'https://www\.', url):
        if re.match(r'www\.', url):
            url = ''.join(['https://', url])
        else:
            url = ''.join(['https://www.', url])
    
    # Get the recipe from the page
    with requests.get(url) as f:
        parser = RecipeHTMLParser(source)
        parser.feed(f.text)
        return parser.recipe
