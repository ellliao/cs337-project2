# cs337-project2
CS 337 Project 2: An interactive recipe chatbot.

##Instructions on pip install file
For recipe_chatbox.py:

- !python -m spacy download en_core_web_md

- !pip install nltk

##Packages Import
For recipe_chatbox.py:

- import nltk

- nltk.download('punkt_tab')

- import re

- import util as u

- from parser import get_recipe_from_url

For recipe_chatbox_testing.ipynb:

- import recipe_chatbox as rc
 
- from parser import get_recipe_from_url

For recipe.py:

- from copy import deepcopy
  
- from fractions import Fraction
  
- from util import nlp, NounType, str_to_fraction

For util.py:

- import re

- import spacy

- import unicodedata

- from enum import Enum, auto

- from fractions import Fraction

- from nltk.corpus import wordnet as wn

##Files input
recipe_chatbox.py:

- util.py

- parser.py

recipe_chatbox_testing:

- recipe_chatbox.py

- parser.py
 
##GitHub repository [https://github.com/ellliao/cs337-project1.git](https://github.com/ellliao/cs337-project2.git)
