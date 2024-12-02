from transformers import pipeline

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline('sentiment-analysis')

def preprocess_text(text: str) -> str:
    """
    Preprocesses the input text by converting to lowercase and stripping whitespace.

    Args:
        text (str): The raw text to preprocess.

    Returns:
        str: The preprocessed text.
    """
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    return text.strip().lower()


def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of the given text using a pre-trained model.

    Args:
        text (str): The text to analyze.

    Returns:
        dict: A dictionary containing the label ('POSITIVE', 'NEGATIVE', 'NEUTRAL') and the confidence score.
    """
    preprocessed_text = preprocess_text(text)
    result = sentiment_pipeline(preprocessed_text)[0]
    return {
        'label': result['label'],
        'score': round(result['score'], 4)  # Rounded to 4 decimal places for clarity
    }


# Example Usage (Comment out in production)
if __name__ == "__main__":
    sample_texts = [
        "I love this product! It's amazing.",
        "This is the worst service I have ever experienced.",
        "The product is okay, but it could be better."
    ]

    for text in sample_texts:
        sentiment = analyze_sentiment(text)
        print(f"Text: {text}")
        print(f"Sentiment: {sentiment}\n")
