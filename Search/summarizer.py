import openai

def summarize(text_context, api_key):
    prompt = f"Summarize the following text in 2-3 sentences:\n\n{text_context}"
    oa = openai.OpenAI(api_key=api_key)
    response = oa.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a summarizer for a search engine."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )
    return response.choices[0].message.content
