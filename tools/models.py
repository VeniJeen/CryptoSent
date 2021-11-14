from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

def distil_bert(x):
    tokens = tokenizer.encode_plus(x, add_special_tokens=True,return_tensors='pt')
    outputs = model(**tokens)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return probs


def test_function():
    pass
