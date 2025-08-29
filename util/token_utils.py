import tiktoken

def count_tokens(text, model="gpt-4"):
    """
    Count the number of tokens in a text string for a given model.
    
    Args:
        text (str): The text to count tokens for
        model (str): The model name to use for tokenization (default: "gpt-4")
    
    Returns:
        int: The number of tokens in the text
    """
    try:
        # Get the encoding for the specified model
        encoding = tiktoken.encoding_for_model(model)
        # Encode the text and return the number of tokens
        return len(encoding.encode(text))
    except Exception:
        # Fallback to a default encoding if model-specific encoding fails
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            # If all else fails, return a rough estimate (4 characters per token)
            return len(text) // 4 if text else 0

def calculate_usage(prompt_text, completion_text, model="gpt-4"):
    """
    Calculate token usage for prompt and completion.
    
    Args:
        prompt_text (str): The prompt text
        completion_text (str): The completion text
        model (str): The model name to use for tokenization (default: "gpt-4")
    
    Returns:
        dict: A dictionary containing prompt_tokens, completion_tokens, and total_tokens
    """
    prompt_tokens = count_tokens(prompt_text, model)
    completion_tokens = count_tokens(completion_text, model)
    total_tokens = prompt_tokens + completion_tokens
    
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens
    }