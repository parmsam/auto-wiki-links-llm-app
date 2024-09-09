from shiny import App, ui, render, reactive
import re
import urllib.parse
import urllib3
from openai import OpenAI
import os

try:
    from setup import api_key1
except ImportError:
    api_key1 = os.getenv("OPENAI_API_KEY")
    
app_info = """
This app takes a body of text and adds Wikipedia links 
to important keywords in the text. It uses the OpenAI API to determine
the important keywords and then checks if a Wikipedia page exists for
each keyword. If a Wikipedia page exists, the keyword is replaced with
a link to the Wikipedia page. The text is markdown formatted. 
"""

default_text = """
Evangelion is set 15 years after a worldwide cataclysm in the futuristic 
fortified city of Tokyo-3. The protagonist is Shinji Ikari, a teenage boy 
recruited by his father Gendo to the mysterious organization Nerv. Shinji 
must pilot an Evangelion, a giant biomechanical mecha, and fight beings known 
as Angels.
"""
    
app_ui = ui.page_fluid(
    ui.h1("Text to Markdown with Wikipedia Links"),
    ui.input_password(
        "api_key", 
        "OpenAI API Key",
        value = api_key1,
    ),
    ui.input_text_area(
        "text_input", 
        "Enter your text:", 
        rows=5, 
        width = "100%",
        value = default_text,
    ),
    ui.output_ui("markdown_output"),
    ui.input_action_button("generate", "Generate Markdown"),
    ui.input_action_button("copy", "Copy to Clipboard", class_="btn-primary"),
    ui.tags.script(
        """
        $(function() {
            Shiny.addCustomMessageHandler("copy_to_clipboard", function(message) {
                navigator.clipboard.writeText(message.text);
            });
        });
        """
    ),
)

def server(input, output, session):
    processed_text = reactive.Value("")
    http = urllib3.PoolManager()

    def get_wikipedia_url(keyword):
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://en.wikipedia.org/wiki/{encoded_keyword}"
        response = http.request('HEAD', url)
        return url if response.status == 200 else None

    def extract_keywords(text):
        api_key = input.api_key()
        if not api_key:
            ui.notification_show(
                "Please enter your OpenAI API key.", 
                type="error"
            )
            return
        client = OpenAI(api_key=api_key)
        prompt = f"""Extract important keywords from the following 
        text:\n\n{text}"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a highly 
                     proficient assistant tasked with determining which words
                     are most important in the text. Please just list the 
                     keywords ina comma-separated list below."""},
                    {"role": "user", "content": prompt,},
                ]
            )
            response_data = response.choices[0].message.content
            keywords = response_data.strip().split(',')
            ui.notification_show(
                f"""Success! Keywords extracted from body of text.""", 
                type="success"
            )
            return [keyword.strip() for keyword in keywords if keyword.strip()]
        except Exception as e:
            ui.notification_show(f"Error: {str(e)}", type="error")

    @reactive.Calc
    @reactive.event(input.generate)
    def process_text():
        text = input.text_input()
        if not text:
            return text
        keywords = extract_keywords(text)
        
        for word in keywords:
            wiki_url = get_wikipedia_url(word)
            if wiki_url:
                text = re.sub(
                    r'\b' + re.escape(word) + r'\b',
                    f"[{word}]({wiki_url})",
                    text,
                    flags=re.IGNORECASE
                )
        
        return text

    @output
    @render.ui
    def markdown_output():
        x = process_text()
        processed_text.set(x)
        return ui.markdown(x)
    
    @reactive.effect
    @reactive.event(input.copy)
    async def _():
        if processed_text.get() != "":
            ui.notification_show("Text copied to clipboard!", duration=3)
            await session.send_custom_message(
                "copy_to_clipboard", 
                {"text": processed_text.get()}
            )
        else:
            ui.notification_show("No text to copy!", type="warning", duration=3)

app = App(app_ui, server)
