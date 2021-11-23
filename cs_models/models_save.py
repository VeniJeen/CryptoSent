from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch



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







from transformers import BertForSequenceClassification, BertTokenizer

# initialize our model and tokenizer
tokenizer_fin_bert_long = BertTokenizer.from_pretrained('ProsusAI/finbert')
model_fin_bert_long = BertForSequenceClassification.from_pretrained('ProsusAI/finbert')

# and we will place the processing of our input text into a function for easier prediction later
def sentiment(tokens):
    # get output logits from the model
    output = model_fin_bert_long(**tokens)
    # convert to probabilities
    probs = torch.nn.functional.softmax(output[0], dim=-1)
    # we will return the probability tensor (we will not need argmax until later)
    return probs


def fin_bert_long(x, output='probs'):
    """
    Return postitive negative neutural
    """
    tokens = tokenizer_fin_bert_long.encode_plus(x, add_special_tokens=False)
    if len(tokens['input_ids'])<512:
        print('i am in the first it')
        outputs = model_fin_bert_long(**tokens)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pos,neg,neut = probs[0][0].item(), probs[0][1].item(), probs[0][2].item()
        return pos,neg,neut
    else:
        print('i am in the else case')
        input_ids = tokens['input_ids']
        attention_mask = tokens['attention_mask']
        # define our starting position (0) and window size (number of tokens in each chunk)
        start = 0
        window_size = 512

        # get the total length of our tokens
        total_len = len(input_ids)

        # initialize condition for our while loop to run
        loop = True

        # loop through and print out start/end positions
        while loop:
            # the end position is simply the start + window_size
            end = start + window_size
            # if the end position is greater than the total length, make this our final iteration
            if end >= total_len:
                loop = False
                # and change our endpoint to the final token position
                end = total_len
            #print(f"{start=}\n{end=}")
            # we need to move the window to the next 512 tokens
            start = end
        # initialize probabilities list
        probs_list = []

        start = 0
        window_size = 510  # we take 2 off here so that we can fit in our [CLS] and [SEP] tokens

        loop = True

        while loop:
            end = start + window_size
            if end >= total_len:
                loop = False
                end = total_len
            # (1) extract window from input_ids and attention_mask
            input_ids_chunk = input_ids[start:end]
            attention_mask_chunk = attention_mask[start:end]
            # (2) add [CLS] and [SEP]
            input_ids_chunk = [101] + input_ids_chunk + [102]
            attention_mask_chunk = [1] + attention_mask_chunk + [1]
            # (3) add padding upto window_size + 2 (512) tokens
            input_ids_chunk += [0] * (window_size - len(input_ids_chunk) + 2)
            attention_mask_chunk += [0] * (window_size - len(attention_mask_chunk) + 2)
            # (4) format into PyTorch tensors dictionary
            input_dict = {
                'input_ids': torch.Tensor([input_ids_chunk]).long(),
                'attention_mask': torch.Tensor([attention_mask_chunk]).int()
            }
            # (5) make logits prediction
            outputs = model_fin_bert_long(**input_dict)
            # (6) calculate softmax and append to list
            probs = torch.nn.functional.softmax(outputs[0], dim=-1)
            probs_list.append(probs)

            start = end
            
        stacks = torch.stack(probs_list)
        shape = stacks.shape

        with torch.no_grad():
            # we must include our stacks operation in here too
            stacks = torch.stack(probs_list)
            # now resize
            stacks = stacks.resize_(stacks.shape[0], stacks.shape[2])
            # finally, we can calculate the mean value for each sentiment class
            mean = stacks.mean(dim=0)
        #pos,neg,neut = mean[0][0].item(), mean[0][1].item(), mean[0][2].item()
        return mean
