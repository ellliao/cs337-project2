# cs337-project2
CS 337 Project 2: An interactive recipe chatbot.

## Setup

### Prerequisites

Before proceeding with setup, you must have the following installed:

* **Python >=3.10**
* **Pip**

### Package installation

To download the required packages for this project, run the following command from within your cloned project directory:
```
pip install -r requirements.txt
```

## Running the Recipe Chatbox

To activate the chatbot, run the following command from within the project directory:
```
python recipe_chatbox.py
```

You can then follow Recipe Chatbox's prompts to interact with it.

The chatbot will display a guide like this

```
1. Walk through the steps

2. Get the list of ingredients
```

Enter '1' to display the next step:
```
Do you have any questions regarding this step?
```

Enter '2' to show the ingredients for the recipe:
```
The ingredients for 'Moussaka' are as follows:
```

Enter 'shortcuts' to view all available keyword shortcuts or ask any other questions you have:
```
Shortcuts:
  • 'shortcuts': Display all avalable keyword shortcuts.
  • '1': Display the next step in current recipe.
  • '2': Display the current recipe's ingredients list.
  • 'quit': End the Recipe Chatbox session.
  • 'new': Start on a different recipe.
```

Enter "How do I do that?" after next step, it will give you a yourtube video link to teach you:
```
Would you like to walk through the steps, or do you have any other questions?
Enter 'shortcuts' to view all available keyword shortcuts or ask any other questions you have
You: 1
Step 1: Lay eggplant slices on paper towels.
Do you have any questions regarding this step?
Enter 'shortcuts' to view all available keyword shortcuts or ask any other questions you have
You: how to do that?
For more details about how to 'lay', visit: https://www.youtube.com/results?search_query=how+do+I+lay+in+the+context+of+cooking
```

Enter "How do I <specific technique>?", it will provide a youtube video to teach you
```
You: how do I crush garlic
For more details, visit: https://www.youtube.com/results?search_query=how+do+i+crush+garlic+in+the+context+of+cooking
```

Navigation utterances enter:
```
"Go back one step", "Go to the next step", "Repeat please", "Take me to the 1st step", "Take me to the n-th step")
```

Enter "what is" questions ("What is a <tool being mentioned>?"):
```
You: what is fork?
For more details, visit: https://www.google.com/search?q=what+is+fork?+in+the+context+of+cooking
Enter 'shortcuts' to view all available keyword shortcuts
```

Asking about the parameters of the current step ("How much of <ingredient> do I need?", "What temperature?", "How long do I <specific technique>?", "When is it done?", "What can I use instead of <ingredient or tool>")

## GitHub repository
[https://github.com/ellliao/cs337-project1.git](https://github.com/ellliao/cs337-project2.git)
