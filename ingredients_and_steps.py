

import requests
from bs4 import BeautifulSoup
import json

def get_recipe_details(url):
    try:
        # Determine the site based on the URL
        if "allrecipes.com" in url:
            site = "allrecipes"
        elif "seriouseats.com" in url:
            site = "seriouseats"
        elif "epicurious.com" in url:
            site = "epicurious"
        else:
            return {"error": "Unsupported site"}

        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the appropriate JSON-LD script tag based on the site
        if site == "allrecipes":
            script_tag = soup.find("script", type="application/ld+json")
        elif site == "seriouseats":
            script_tag = soup.find("script", id="schema-lifestyle_1-0", type="application/ld+json")
        elif site == "epicurious":
            script_tag = soup.find("script", type="application/ld+json")

        if not script_tag:
            return {"error": "Could not find the JSON-LD script"}

        # Load the JSON content from the script tag
        recipe_data = json.loads(script_tag.string)

        # Check if the data is a list of objects or a single object
        if isinstance(recipe_data, list):
            # Filter for the object of type "Recipe"
            recipe_data = next((item for item in recipe_data if "Recipe" in item["@type"]), None)

        if not recipe_data:
            return {"error": "Recipe data not found"}

        # Extract the recipe name
        name = recipe_data.get("name", "Unknown Recipe")

        # Extract the ingredients list
        ingredients = recipe_data.get("recipeIngredient", [])

        # Extract the directions (instructions)
        instructions = []
        recipe_instructions = recipe_data.get("recipeInstructions", [])
        for step in recipe_instructions:
            if isinstance(step, dict) and step.get("@type") == "HowToStep":
                text = step.get("text", "").strip()
                if text:
                    instructions.append(text)

        return {
            "name": name,
            "ingredients": ingredients,
            "directions": instructions
        }

    except Exception as e:
        return {"error": str(e)}
    
url_test_list = [
    "https://www.allrecipes.com/recipe/19547/grandmas-corn-bread-dressing/",
    "https://www.seriouseats.com/beef-braciole-recipe-7561806",
    "https://www.epicurious.com/recipes/food/views/ba-syn-brussels-sprouts-stir-fry-cheddar-golden-raisins",
    "https://www.allrecipes.com/recipe/239960/fresh-cranberry-sauce/",
    "https://www.allrecipes.com/recipe/18379/best-green-bean-casserole/",
    "https://www.allrecipes.com/recipe/256288/chef-johns-creamy-corn-pudding/",
    "https://www.seriouseats.com/plum-infused-water-recipe-7560513",
    "https://www.seriouseats.com/scallop-crudo-recipe-7566506",
    "https://www.epicurious.com/recipes/food/views/ba-syn-haitian-bouillon-bouyon"
]

# Loop through the URL list and print the details for each recipe
for url in url_test_list:
    recipe_details = get_recipe_details(url)
    name = recipe_details.get("name", "Unknown Recipe")
    ingredients = recipe_details.get("ingredients", [])
    directions = recipe_details.get("directions", [])
    error = recipe_details.get("error")

    print(f"\nRecipe Name: {name}")
    if error:
        print(f"Error: {error}")
    else:
        print("\nIngredients:")
        for ingredient in ingredients:
            print(f"- {ingredient}")

        print("\nDirections:")
        for i, direction in enumerate(directions, start=1):
            print(f"{i}. {direction}")

    print("-" * 50)
