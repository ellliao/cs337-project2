# cs337-project2
CS 337 Project 2: An interactive recipe chatbot.
##Instructions on pip install file
For recipe_chatbox.py:

!python -m spacy download en_core_web_md

!pip install nltk

##Packages Import
For recipe_chatbox.py:

import nltk

nltk.download('punkt_tab')

import re

import util as u

from parser import get_recipe_from_url

Files input for recipe_chatbox.py:

util.py

parser.py
