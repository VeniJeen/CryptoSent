#from platform import dist
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm
tqdm.pandas()


tokenizer_distil = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model_distil = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

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


def distil_bert_df(df,text,output_type='probs'):
    if output_type == 'probs':
        temp=df[text].progress_apply(lambda x: distil_bert(x,output=output_type));
        #df['neg_db']=temp.apply(lambda x: x[0])
        #df['pos_db']=temp.apply(lambda x: x[1])
        df.loc[:,'neg_db']=temp.apply(lambda x: x[0])
        df.loc[:,'pos_db']=temp.apply(lambda x: x[1])
        return df
    else:
       df['sent_db']=df[text].progress_apply(lambda x: distil_bert(x,output=output_type));
       return df