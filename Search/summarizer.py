import openai
import tiktoken

def truncate_text(text, max_tokens=50000):
    """Truncate text to stay within token limit"""
    try:
        # Use tiktoken for accurate token counting
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = encoding.encode(text)
        
        if len(tokens) > max_tokens:
            # Truncate tokens and decode back to text
            truncated_tokens = tokens[:max_tokens]
            return encoding.decode(truncated_tokens)
        return text
    except Exception:
        # Fallback to character-based truncation (approximation)
        char_limit = max_tokens * 4  # Rough estimate of chars per token
        if len(text) > char_limit:
            return text[:char_limit] + "..."
        return text

def summarize(text_context, api_key):
    # Truncate text to avoid exceeding context length
    truncated_text = truncate_text(text_context, max_tokens=50000)
    
    prompt = f"Summarize the following text in 2-3 sentences:\n\n{truncated_text}"
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
