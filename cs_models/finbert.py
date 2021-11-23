from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer_finbert = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model_finbert = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

def fin_bert(x, output='probs'):
    """
    Return postitive negative neutural
    """
    tokens = tokenizer_finbert.encode_plus(x, add_special_tokens=True,return_tensors='pt')
    outputs = model_finbert(**tokens)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    pos,neg,neut = probs[0][0].item(), probs[0][1].item(), probs[0][2].item()
    return pos,neg,neut


