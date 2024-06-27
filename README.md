# LLM for Conversational Group Recommender System

In this project, we aim at exploring the possibility of supporting the group decision-making process using a
virtual assistant, which interacts with the group using a chat-based interface. Group members will be able
to discuss and propose items, in order to find a shared solution; the virtual assistant will process these
information, infer group members’ preferences, and provide suggestions to the group using baseline
aggregation strategies, prompting a ChatGPT with all these information to obtain recommendations and
textual explanations to discuss with the group.

## Current State

The project currently consists of a discord bot that can be used to recommend recipes to a group of people. This is done
by first collecting information on tags (identifiers used to describe the recipes) that users like and dislike and then
using these tags to recommend a recipe to the users.

## Usage

The recommendation module can be run by running the file runner.py in grsmodel/main_runner/runner.py.
to make it work you will have to create a .env folder in that folder in which you add:

* DISCORD_TOKEN -> the token of the discord bot
* PROJECT_ID -> the projectid of the google cloud project through which gemini is used
* PROJECT_LOCATION -> the location of the google cloud project through which gemini is used
* OPEN_AI_API_KEY -> the api key of the open ai api

[https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)
this link contains the raw data used for this project. The data from this is then used data_cleanup.ipynb to generate
2 csv files; cleaned_recipes.csv and cleaned_recipes_with_country.csv. These 2 files should be placed in the main_runner
directory. When all these steps are done the runner.py file can be run.

## Authors

* **Bams Guillaume** - [Guillaume](https://github.com/Guil02) - Developer
* **Beuk Jiska** - [Jiska](https://github.com/jiskabeuk) - Developer
* **Karça Cavid** - [Cavid](https://github.com/Caviid) - Developer
* **Leonidas Alexander** - [Alexander](https://github.com/alexanderleonidas) - Developer
* **Passos Patrício Ferreira Tiago** - [Tiago](https://github.com/Tpf2906) - Developer
* **Pompigna Lorenzo** - [Lorenzo](https://github.com/Lozzio99) - Developer
