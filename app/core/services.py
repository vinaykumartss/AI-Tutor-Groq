from app.core.settings import groq_client
from app.core.prompts import grammar_prompts, sys_msg_prompts, hindi_to_english_translation_prompts, hindi_idiom_to_english_prompt
from app.core.harmful_content import contains_harmful_content

# Global variable to store the conversation history
conversation_history = [{'role': 'system', 'content': sys_msg_prompts()}]

def check_grammar(text: str) -> str:
    grammar_prompt = grammar_prompts(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'system', 'content':grammar_prompt}],
        model='llama3-70b-8192'
    )

    return chat_completion.choices[0].message.content.strip()

def translate_text(text: str) -> str: 
    translation_text = hindi_to_english_translation_prompts(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'user', 'content':translation_text}],
        model='llama3-70b-8192'
    )
    return chat_completion.choices[0].message.content.strip()

def idiom_text(text: str) -> str:
    hindi_to_english_idiom = hindi_idiom_to_english_prompt(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'user', 'content':hindi_to_english_idiom}],
        model='llama3-70b-8192'
    )
    return chat_completion.choices[0].message.content.strip()

def ai_tutor(prompt: str) -> str:

    # convo = [{'role': 'system', 'content': sys_msg_prompts()}]

    if contains_harmful_content(prompt):
        return (
            "I'm sorry, but I cannot respond to harmful or inappropriate content. "
            "I am designed to assist with improving communication skills, providing advice, and enhancing grammar and vocabulary. "
            "Please keep the conversation respectful and focused on these topics."
        )
    
     # Append the user's prompt to the conversation history
    conversation_history.append({'role': 'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(
        messages=conversation_history,
        model='llama3-70b-8192'
    )
    response = chat_completion.choices[0].message
    conversation_history.append(response)
    return response.content