from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch



#tokenizer_distil = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
#model_distil = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

def distil_bert(x, output='probs'):
    """
    Return Negative first and Positive after
    """
    tokens = tokenizer_distil.encode_plus(x, add_special_tokens=True,return_tensors='pt')
    outputs = model_distil(**tokens)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    neg,pos = probs[0][0].item(), probs[0][1].item()
    if output == 'probs':
        return neg,pos
    else:
        return pos-neg




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
