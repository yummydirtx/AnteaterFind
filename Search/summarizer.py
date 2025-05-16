from google import genai

def truncate_text(text, max_tokens=50000):
    """Truncate text to stay within token limit"""
    char_limit = max_tokens * 4  # Rough estimate of chars per token
    if len(text) > char_limit:
        return text[:char_limit] + "..."
    return text

def summarize(text_context, api_key):
    # Truncate text to avoid exceeding context length
    truncated_text = truncate_text(text_context)
    
    prompt = f"\n\n{truncated_text}"
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents = "You are search engine that provides concise summaries of web pages. Your task is to summarize the content of the following text in 2-3 sentences, no need to start with a complete sentence (aka, no need to clarify that you are summarizing a web page). Answer in paragraph form. " + prompt
    )
    return response.text
