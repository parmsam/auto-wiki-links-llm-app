# automatic-wiki-links-llm-app

This is a Shiny for Python app that takes a body of text and adds Wikipedia links 
to important keywords in the text. It uses the OpenAI API to determine
the important keywords and then checks if a Wikipedia page exists for
each keyword. If a Wikipedia page exists, the keyword is replaced with
a link to the Wikipedia page. The link is markdown formatted like this:
`[keyword](https://en.wikipedia.org/wiki/Keyword)`. 

## Setup

The app expects that you have an OpenAI API key that you can paste into the input box. You can get one by visting the OpenAI API [quickstart page](https://platform.openai.com/docs/quickstart/).

## Accessing the app

You can clone this repo and run the app locally or access the app via [Connect Cloud](https://connect.posit.cloud/) at the website link in the repository details (under "About"). You may need to create a Connect Cloud account to access the app.