'''The main chatbot'''
import nltk
nltk.download('punkt_tab')
import re
import util as u

from parser import get_recipe_from_url

###########
# CONTEXT #
###########

class Context:

    def __init__(self):

        self.user_prompts = []
        self.current_recipe = None
        self.current_step = 0

#####################
# DISPLAY FUNCTIONS #
#####################

def display_step(context):

    if context.current_step >= len(context.current_recipe.steps):
        print("Sorry, we have gone through all the steps")

    if context.current_step == len(context.current_recipe.steps) - 1:
        step_text = f"Final Step: {context.current_recipe.steps[context.current_step]}"
    else:
        step_text = f"Step {context.current_step + 1}: {context.current_recipe.steps[context.current_step].text}"


    print(step_text)

    context.current_step += 1


    if context.current_step >= len(context.current_recipe.steps):
        print("/n Do you have any questions regarding this final step?")
        print("You can press '2' for the list of ingredients, "
              "'quit' to end the session, or ask any other questions "
              "you have")
    else:
        print("Do you have any questions regarding this step?")
        print("You can press '1' for the next step, '2' for the list of "
              "ingredients, 'quit' to end the session, or ask any other "
              "questions you have")

def display_ingredients(context):

    recipe_title = context.current_recipe.title
    ingredients = context.current_recipe.ingredients




    if ingredients:
        print(f"The ingredients for '{recipe_title}' are as follows:")

        for ingr in ingredients:

            print(
            '  • ',
            u.fraction_to_str(ingr.quantity) if ingr.quantity else '',
            ' ' if ingr.quantity else '',
            ingr.unit if ingr.unit else '',
            ' ' if ingr.unit else '',
            ingr.name,
            sep=''
        )

    else:
        print(f"Sorry, I could not obtain the ingredients")

    if context.current_step > 0:
        print("\nWould you like to go back to the steps, or do you have any other questions?")
        print("You can press '1' for the next step, '2' for the list of ingredients or 'quit' to end the session or any other questions you have")

    else:
        print("\nWould you like to walk through the steps, or do you have any other questions?")
        print("You can press '1' for the next step, '2' for the list of ingredients or 'quit' to end the session or any other questions you have")

##########################
# SEARCH QUERY FORMATION #
##########################

def generate_youtube_search_url(query):

    base_url = "https://www.youtube.com/results?search_query="
    formatted_query = query.replace(" ", "+")
    return base_url + formatted_query

def generate_google_search_url(query):

    base_url = "https://www.google.com/search?q="
    formatted_query = query.replace(" ", "+")
    return base_url + formatted_query

#################
# INPUT PARSING #
#################

def is_ambiguous(input_string):
    """
    Checks if the input string contains ambiguous references like 'that', 'these', 'this', etc.

    """

    pattern = r'\b(that|this|these|those|it|here|there)\b'

    return bool(re.search(pattern, input_string, re.IGNORECASE))

def contains_what(input_string):

    pattern = r'\bwhat\b'
    return bool(re.search(pattern, input_string, re.IGNORECASE))

def contains_how(input_string):

    pattern = r'\bhow\b'
    return bool(re.search(pattern, input_string, re.IGNORECASE))

def contains_ingredient(input_string):


    pattern = r'\bingredients?\b'
    return bool(re.search(pattern, input_string, re.IGNORECASE))

def is_temperature_related(input_string):

    pattern = r'\b(temperature|hot|cold|warm|cool|heat|degrees?|celsius|fahrenheit|temp|temps)\b'


    return bool(re.search(pattern, input_string, re.IGNORECASE))

def is_duration_related(prompt):

    pattern = r'\b(how long|how many minutes?|time|duration|minutes?|hours?|seconds?|when)\b'

    return bool(re.search(pattern, prompt, re.IGNORECASE))


def is_amount_related(prompt):


    pattern = r'\b(how much|amount|quantity|measure|measurement|portion|serving|use)\b'

    return bool(re.search(pattern, prompt, re.IGNORECASE))

##########################
# INFORMATION EXTRACTION #
##########################

number_map = {
    "zero": 0, "one": 1, "first": 1, "two": 2, "second": 2, "three": 3, "third": 3,
    "four": 4, "fourth": 4, "five": 5, "fifth": 5, "six": 6, "sixth": 6,
    "seven": 7, "seventh": 7, "eight": 8, "eighth": 8, "nine": 9, "ninth": 9,
    "ten": 10, "tenth": 10, "eleven": 11, "eleventh": 11, "twelve": 12, "twelfth": 12,
    "thirteen": 13, "thirteenth": 13, "fourteen": 14, "fourteenth": 14,
    "fifteen": 15, "fifteenth": 15, "sixteen": 16, "sixteenth": 16,
    "seventeen": 17, "seventeenth": 17, "eighteen": 18, "eighteenth": 18,
    "nineteen": 19, "nineteenth": 19, "twenty": 20, "twentieth": 20,
    "thirty": 30, "thirtieth": 30, "forty": 40, "fortieth": 40,
    "fifty": 50, "fiftieth": 50, "sixty": 60, "sixtieth": 60,
    "seventy": 70, "seventieth": 70, "eighty": 80, "eightieth": 80,
    "ninety": 90, "ninetieth": 90, "hundred": 100
}

def extract_step_number(user_input):

    ordinal_match = re.search(r"(\d+)(?:st|nd|rd|th)?", user_input)
    if ordinal_match:
        return int(ordinal_match.group(1))


    user_input = user_input.lower().strip()
    words = re.findall(r'\w+', user_input)  # Split input into words

    total = 0
    current_value = 0

    for word in words:
        if word in number_map:
            value = number_map[word]
            # Handle cases like "twenty-first", "forty-second"
            if value >= 100:
                current_value *= value
            elif current_value >= 20:
                total += current_value
                current_value = value
            else:
                current_value += value

    total += current_value
    return total if total > 0 else None

##################
# ACTION HELPERS #
##################

def repeat_step(context):
    context.current_step -= 1
    display_step(context)

def go_to_step(context, step):
    context.current_step =  step - 1
    display_step(context)

###################
# INTENT HANDLERS #
###################

def handle_what(context, input_text):

    if is_ambiguous(input_text):

        current_step = context.current_recipe.steps[context.current_step - 1]
        queries = []
        result_strings = []


        if isinstance(current_step.methods, list):
            for method in current_step.methods:
                if isinstance(method, str):
                    query = f"{method} as a method of cooking"
                    queries.append(query)
                    result_strings.append(
                        f"For more details about '{method}', visit: {generate_google_search_url(query)}"
                    )


        for ingr in current_step.ingredients:
            if isinstance(ingr.name, str):
                query = ingr.name
                queries.append(query)
                result_strings.append(
                    f"For more details about '{ingr.name}', visit: {generate_google_search_url(query)}"
                )


        if isinstance(current_step.tools, list):
            for tool in current_step.tools:
                if isinstance(tool, str):
                    queries.append(tool)
                    result_strings.append(
                        f"For more details about '{tool}', visit: {generate_google_search_url(tool)}"
                    )


    else:

        query = input_text + " in the context of cooking"
        result_strings = [
            f"For more details, visit: {generate_google_search_url(query)}"
        ]

    result_strings.append(
        "You can press '1' for the next step, '2' for the list of ingredients, "
        "or 'quit' to end the session or any other questions you have."
    )

    return "\n".join(result_strings)

def handle_how(context, input_text):
    tq = "How to"
    hd = "how do I do that"
    if tq in input_text:
        w = input_text.split(tq, 1)[1].strip()
        return f"Here is relevant Video Link: {generate_youtube_search_url(w)}"
    elif hd in input_text:
        current_step = context.current_recipe.steps[context.current_step - 1]
        if current_step.methods:
            FM = current_step.methods[0]
            query = f"How do I {FM} for the cooking"
            return f"{FM}: Link-- {generate_youtube_search_url(query)}"
    else:
        None

    if is_ambiguous(input_text):

        current_step = context.current_recipe.steps[context.current_step - 1]
        result_strings = []


        if isinstance(current_step.methods, list):
            for method in current_step.methods:
                if isinstance(method, str):
                    query = f"how do I {method} in the context of cooking"
                    result_strings.append(
                        f"For more details about how to '{method}', visit: {generate_youtube_search_url(query)}"
                    )
    else:

        query = f"{input_text} in the context of cooking"
        result_strings = [
            f"For more details, visit: {generate_youtube_search_url(query)}"
        ]

    result_strings.append(
        "You can press '1' for the next step, '2' for the list of ingredients, "
        "or 'quit' to end the session or any other questions you have."
    )
    return "\n".join(result_strings)

def handle_temperature(context):

    current_step = context.current_recipe.steps[context.current_step - 1]


    result_strings = []
    if current_step.temps:

        result_strings.append( f"Temperature : {', '.join(current_step.temps)}" )
    else:

        method = ', '.join(current_step.methods) if current_step.methods else current_step.text
        query = f"At what temperature should I {method} when preparing {context.current_recipe.title}"
        result_strings.append( f"No temperature specified. For more details, visit: {generate_google_search_url(query)}")

    return "\n".join(result_strings)



def handle_duration(context):


    current_step = context.current_recipe.steps[context.current_step - 1]


    result_strings = []
    if current_step.times:

        result_strings.append(f"Duration: {', '.join(current_step.times)}")
    else:
        method = ', '.join(current_step.methods) if current_step.methods else current_step.text
        query = f"How long should I {method} when preparing {context.current_recipe.title}"
        result_strings.append(f"No duration specified. For more details, visit: {generate_google_search_url(query)}")

    return "\n".join(result_strings)


def handle_amount(context, prompt):

    current_step = context.current_recipe.steps[context.current_step - 1]  # Convert 1-based index to 0-based
    mentioned_ingredients = []

    # Check if the prompt mentions any ingredient from the step
    for ingredient in current_step.ingredients:
        if ingredient.name and re.search(rf'\b{re.escape(ingredient.name)}\b', prompt, re.IGNORECASE):
            mentioned_ingredients.append(ingredient)

    result_strings = []

    if mentioned_ingredients:

        for ingredient in mentioned_ingredients:
            quantity = ingredient.quantity if ingredient.quantity else "some"
            unit = ingredient.unit if ingredient.unit else ""
            result_strings.append(f"Use {quantity} {unit} of {ingredient.name}.")
    else:

        for ingredient in current_step.ingredients:
            quantity = ingredient.quantity if ingredient.quantity else "some"
            unit = ingredient.unit if ingredient.unit else ""
            result_strings.append(f"Use {quantity} {unit} of {ingredient.name}.")

    return "\n".join(result_strings)

def handle_navigations(context, user_input):

    doc = u.nlp(user_input.lower())

    # Extract the main action verb
    action = None
    for token in doc:
        if token.pos_ == "VERB":
            action = token.lemma_
            break

    # Determine the intent based on the verb
    if action == "repeat":
        repeat_step( context)
        return

    if action in ["go", "take"]:
        # Check for "go back", "previous", or "back"
        if any(word in user_input for word in ["back", "previous"]):
            step_number = None

            step_check_pattern = pattern = r"\bstep\b"
            if re.search(step_check_pattern, user_input, re.IGNORECASE) is not None:
                input_number = extract_step_number(user_input)
                if not input_number:
                    step_number = context.current_step - 1
                else:
                    step_number = input_number
            else:
                input_number = extract_step_number(user_input) or 1
                step_number = context.current_step - input_number
            go_to_step(context, step_number)
            return

        # Check for "next step" or "forward"
        if "next" in user_input or "forward" in user_input:
            input_number = extract_step_number(user_input) or 1
            step_number = context.current_step + input_number
            go_to_step(context, step_number)
            return

        # Check for specific step (e.g., "go to the 5th step")
        step_number = extract_step_number(user_input)
        if step_number:
            if 1 <= step_number <= len(context.current_recipe.steps):
                go_to_step(context, step_number)
            else:
                print("Invalid step number.")
            return


    return

#################
# INPUT HANDLER #
#################

def handle_input(context, user_input):

    if contains_ingredient(user_input):

        display_ingredients(context)
        return

    if is_temperature_related(user_input):

        handle_temperature(context)
        return
    if is_amount_related(user_input):
        handle_amount(context, user_input)
        return
    if is_duration_related(user_input):
        handle_duration(context)
        return



    if contains_what(user_input):
        result = handle_what(context, user_input)
        print(result)
        return

    if contains_how(user_input):
        result = handle_how(context, user_input)
        print(result)
        return

    handle_navigations(context, user_input)

#############
# INTERFACE #
#############

def CI(new_session: bool = True):

  context = Context()
  if new_session:
    print("Welcome to Recipe Chatbox! ", end='')
  print("Please enter the URL of the recipe you need assistance with.")
  recipe = None

  while (not recipe ):

        user_L = input("Input the Link here: ") #user input here for link
        print(user_L)


        context.user_prompts.append(f"Link: {user_L}") # store user input link
        recipe = get_recipe_from_url(user_L)#parser to get the link content
        context.current_recipe = recipe

        if recipe:
          continue
        else:
          print("Invalid url, please try again. ")


  print(f"Got it! I'm ready to assist with the recipe for '{recipe.title}'.")
  print("Would you like to:")
  print("1. Walk through the steps")
  print("2. Get the list of ingredients")
  print("Type 'quit' to end the session, 'new' to start on a different "
        "recipe, or ask any other requests.")

  while True:

    user_prompt = input("You: ").strip().lower()

    if user_prompt == "1":
      context.user_prompts.append("1: Walk through the steps")
      display_step( context)

    elif user_prompt == "2":
      context.user_prompts.append("2: Get the list of ingredients")
      display_ingredients(context)

    elif user_prompt == "quit" or \
        re.findall(r'\b(?:end|stop)\b.*\b(?:session|program|script)\b'
                   r'|\bquit\b|\bexit\b',
                   user_prompt, re.IGNORECASE):
      context.user_prompts.append("quit")
      print("Thank you for using the Recipe Chatbox. Have a great day!")
      break

    elif user_prompt == "new" or \
        re.findall(r'\b(?:new|another|different) recipe\b',
                   user_prompt, re.IGNORECASE):
        CI(False)
        return


    else:
      handle_input(context,user_prompt)


if __name__ == "__main__":
    CI()
