from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')

finbert_tone = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer)

def finbert_tone_model(txt):
    try: 
        return finbert_tone(txt)
    except:
        return 'no_result'