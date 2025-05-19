# Latih lagi modelnya agar lebih baik 🙏

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd

# Load model dan tokenizer
def load_model_pipeline():
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    #tokenizer_model = "indobenchmark/indobert-base-p1"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    return sentiment_pipeline

# Fungsi prediksi satu komentar
def predict_sentiment(text, pipeline_model):
    result = pipeline_model(text)[0]
    return result['label'], result['score']

# Proses semua komentar dalam DataFrame
def analyze_sentiment(df, text_column="Komentar"):
    pipeline_model = load_model_pipeline()
    
    sentiments = df[text_column].apply(lambda x: predict_sentiment(x, pipeline_model))
    
    # Pisahkan jadi dua kolom
    df[['Label Sentimen', 'confidence']] = pd.DataFrame(sentiments.tolist(), index=df.index)
    
    # Mapping label
    label_mapping = {
        'LABEL_0': 'Negatif',
        'LABEL_1': 'Netral',
        'LABEL_2': 'Positif'
    }
    df['Label Sentimen'] = df['Label Sentimen'].map(label_mapping)
    
    return df
