import praw
from psaw import PushshiftAPI
from dateutil import parser
import datetime as dt
import pandas as pd
from update_checker import UpdateResult
import zstandard
import json
import time
import datetime
from os import listdir
from os.path import isfile, join
import ast


def test():
    print('aa23a')

def get_awards(x):
    """
    Extracting all_awardings award's: Name, Description, Count, Coin Price, Coin Reward
    """
    if x == 'Empty':
        return 'Empty'
    else:
        try:
            save_list=[]
            awards_list=ast.literal_eval(x)
            for award in awards_list:
                save_list.append([award['name'],award['description'],award['count'],award['coin_price'],award['coin_reward']])
            return save_list
        except:
            return 'Empty'


def merge_submissions(data_bank_path):
    """
    Merging the submissions monthly files from the Dataset Bank
    Additionaly filtering on features
    """
    path=data_bank_path
    files = [path+"""\\""" +f for f in listdir(path) if isfile(join(path, f))]
    keep_cols_sub=['all_awardings','author','author_created_utc','author_fullname','created_utc','domain','id',
            'domain','num_comments','no_follow','permalink','score','selftext',
            'send_replies','subreddit','subreddit_id','subreddit_subscribers','title','url']    

    df_merged=pd.DataFrame()
    for index,file in enumerate(files):
            if index == 0 or index == 1:
                    "First two files dont have all_awardings feature"
                    temp=pd.read_csv(file, low_memory=False)
                    temp['all_awardings']='Empty'
                    df_merged=pd.concat([df_merged,temp[keep_cols_sub]])
            else:
                    df_merged=pd.concat([df_merged,pd.read_csv(file, low_memory=False)[keep_cols_sub]])

    df_merged=df_merged.drop_duplicates()
    df_merged.all_awardings=df_merged.all_awardings.replace({'[]':'Empty'})
    df_merged.all_awardings=df_merged.all_awardings.apply(lambda x: 'Empty' if x=='Empty' else get_awards(x))
    return df_merged

def merge_comments(data_bank_path):
    """
    Merging the comments monthly files from the Dataset Bank
    Additionaly filtering on features
    """
    path=data_bank_path
    files = [path+"""\\""" +f for f in listdir(path) if isfile(join(path, f))]
    keep_cols_com=['all_awardings','author','author_created_utc','author_fullname','author_flair_text','body','created_utc',
               'distinguished','id','is_submitter','no_follow','link_id','parent_id','permalink',
               'score','subreddit','subreddit_id']

    df_merged=pd.DataFrame()
    for index,file in enumerate(files):
            if index == 0 or index == 1:
                    "First two files dont have all_awardings feature"
                    temp=pd.read_csv(file, low_memory=False)
                    temp['all_awardings']='Empty'
                    df_merged=pd.concat([df_merged,temp[keep_cols_com]])
            else:
                    df_merged=pd.concat([df_merged,pd.read_csv(file, low_memory=False)[keep_cols_com]])

    df_merged=df_merged.drop_duplicates()
    df_merged.all_awardings=df_merged.all_awardings.replace({'[]':'Empty'})
    df_merged.all_awardings=df_merged.all_awardings.apply(lambda x: 'Empty' if x=='Empty' else get_awards(x))
    return df_merged






def get_submissions_raw(): return pd.read_csv(
    r"C:\Users\Ben\Desktop\Diplomatiki\CryptoSent\Datasets\Main Dataset\submissions_2019__2021_06.csv")


def get_comments_raw(): return pd.read_csv(
    r"C:\Users\Ben\Desktop\Diplomatiki\CryptoSent\Datasets\Main Dataset\comments_2019__2021_06.csv")


def date_parser_utc(x): return dt.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')



awards_attribute_dict={'name':0,
                       'description':1,
                       'count':2,
                       'coin_price':3,
                       'coin_reward':4}

def award_extraction(x,att):
    if x=='Empty': return 'Empty'
    elif len(x)==1:return x[0][awards_attribute_dict[att]]
    else: return list(zip(*x))[awards_attribute_dict[att]]



def submission_raw_processing(s):
    """
    input get_submission_raw for first level processing
    """
    crypto_subreddits=['Bitcoin','CryptoCurrency','btc','CryptoMarkets','bitcoinbeginners',
                   'CryptoCurrencies','altcoin','icocrypto','CryptoCurrencyTrading','Crypto_General',
                   'ico','blockchain','ethereum','Ripple','litecoin','Monero','Stellar','CryptoCurrencyClassic']
                   
    s=s[s.subreddit.isin(crypto_subreddits)]
    s=s.loc[:,~s.columns.duplicated()]

    s['award_name']=s.all_awardings.apply(lambda x: award_extraction(x,'name'))
    s['award_description']=s.all_awardings.apply(lambda x: award_extraction(x,'description'))
    s['award_count']=s.all_awardings.apply(lambda x: award_extraction(x,'count'))
    s['award_coin_price']=s.all_awardings.apply(lambda x: award_extraction(x,'coin_price'))
    s['award_coin_reward']=s.all_awardings.apply(lambda x: award_extraction(x,'coin_reward'))


    try:
        # col drop
        s = s.drop(columns=['Unnamed: 0', 'domain.1'])
    except:
        pass

    # cols order
    cols_order_subs = ['created_utc', 'author',
                       'num_comments', 'score', 'title', 'selftext',
                       'award_name','award_description','award_count',
                       'award_coin_price','award_coin_reward',
                       'subreddit', 'subreddit_subscribers', 'id',
                       'domain', 'no_follow',
                       'send_replies', 'author_created_utc', 'author_fullname',
                       'subreddit_id',
                       'permalink', 'url']

    s = s[cols_order_subs]

    # parsing utc dates
    s['created'] = s.created_utc.apply(date_parser_utc)
    s['created'] = pd.to_datetime(s.created)
    s.index = s.created
    s['author_created'] = s.author_created_utc.fillna(1461114906).apply(date_parser_utc)
    s['author_created'] = pd.to_datetime(s.author_created)
    s.loc[s['author_created'] == date_parser_utc(1461114906), 'author_created'] = None

    # drop utc dates
    s = s.drop(columns=['created_utc', 'author_created_utc'])

    # define categories for lower ram usage
    # s.subreddit=s.subreddit.astype('category')
    s.domain = s.domain.astype('category')
    s.no_follow = s.no_follow.astype('category')
    s.send_replies = s.send_replies.astype('category')
    s.subreddit_id = s.subreddit_id.astype('category')
    return s


def comments_raw_processing(s):
    """
    input get_submission_raw for first level processing
    """
    crypto_subreddits=['Bitcoin','CryptoCurrency','btc','CryptoMarkets','bitcoinbeginners',
                   'CryptoCurrencies','altcoin','icocrypto','CryptoCurrencyTrading','Crypto_General',
                   'ico','blockchain','ethereum','Ripple','litecoin','Monero','Stellar','CryptoCurrencyClassic']
                   
    s=s[s.subreddit.isin(crypto_subreddits)]
    s=s.loc[:,~s.columns.duplicated()]

    s['award_name']=s.all_awardings.apply(lambda x: award_extraction(x,'name'))
    s['award_description']=s.all_awardings.apply(lambda x: award_extraction(x,'description'))
    s['award_count']=s.all_awardings.apply(lambda x: award_extraction(x,'count'))
    s['award_coin_price']=s.all_awardings.apply(lambda x: award_extraction(x,'coin_price'))
    s['award_coin_reward']=s.all_awardings.apply(lambda x: award_extraction(x,'coin_reward'))
    s=s.drop(columns='all_awardings')

    try:
        # col drop
        s = s.drop(columns=['Unnamed: 0', 'domain.1'])
    except:
        pass



    # parsing utc dates
    s['created'] = s.created_utc.apply(date_parser_utc)
    s['created'] = pd.to_datetime(s.created)
    s.index = s.created
    s['author_created'] = s.author_created_utc.fillna(1461114906).apply(date_parser_utc)
    s['author_created'] = pd.to_datetime(s.author_created)
    s.loc[s['author_created'] == date_parser_utc(1461114906), 'author_created'] = None

    # drop utc dates
    s = s.drop(columns=['created_utc', 'author_created_utc'])

    # define categories for lower ram usage
    # s.subreddit=s.subreddit.astype('category')
    #s.domain = s.domain.astype('category')
    s.no_follow = s.no_follow.astype('category')
    #s.send_replies = s.send_replies.astype('category')
    s.subreddit_id = s.subreddit_id.astype('category')
    return s



def date_decomposition(s):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    s['year'] = s.created.dt.year.values
    s['month'] = s.created.dt.month.values
    s['month_name'] = s.created.dt.month_name().str.slice(stop=3)
    s['month_name'] = pd.Categorical(s['month_name'], categories=months, ordered=True)
    s['day'] = s.created.dt.day.values
    s['day_name'] = s.created.dt.day_name().values
    s['day_name'] = pd.Categorical(s['day_name'], categories=days, ordered=True)
    s['week'] = s.created.dt.isocalendar().week.values
    s['day_of_week'] = s.created.dt.dayofweek.values
    s['hour'] = s.created.dt.hour.values
    s['minute'] = s.created.dt.minute.values
    return s


def decompose_zstd_streaming(zst_files, subreddits_list):
    """
    Streaming decomposision function from PlusShift Database    
    """
    for file_no, zst_file_path in enumerate(zst_files):
        slist = []
        df_out = pd.DataFrame()
        count = 0
        chunk_count = 0
        iteration = 0
        program_starts = time.time()
        name = zst_file_path.split('\\')[-1].split('.')[0]
        print('\nProcessing File:', name, '  ', file_no + 1, '/', len(zst_files))
        with open(zst_file_path, 'rb') as fh:
            dctx = zstandard.ZstdDecompressor(max_window_size=2147483648)
            with dctx.stream_reader(fh) as reader:
                previous_line = ""
                while True:
                    now = time.time()
                    chunk = reader.read(2 ** 24)  # 16mb chunks
                    chunk_count += 1
                    if not chunk:
                        break

                    string_data = chunk.decode('utf-8')
                    lines = string_data.split("\n")
                    for i, line in enumerate(lines[:-1]):
                        if i == 0:
                            line = previous_line + line
                        object_chunk = json.loads(line)
                        count += 1

                        if any(object_chunk['subreddit'] in s for s in subreddits_list):
                            slist.append(object_chunk)
                    if divmod(count, 5000000)[0] > iteration:
                        iteration = divmod(count, 5000000)[0]
                        print('')
                        print("|t:", str(datetime.timedelta(seconds=(now - program_starts))).split('.')[0],
                              '|\t|Saved Rows:', len(slist) / 1000, 'K',
                              '|\t|Raw Rows:', count / 1000, 'K',
                              '|\t|', chunk_count * 16, 'MB Proccesed|')
                    # if count > 800000: break
                    previous_line = lines[-1]

        df_out = pd.DataFrame(slist)
        df_out.to_csv(f'{name}_crypto_subreddits.csv')


# Connecting to Reddit API
def access_reddit():
    """
    Connecting to Reddit API
    """
    reddit = praw.Reddit(client_id="f0b33JSRVGyB8p-ua4_58g",  # my client id
                         client_secret="H6vEPyKbzDASg9G5hlAi7WoKdAE58g",  # your client secret
                         user_agent="Scraping Script 101 by u/Icy_Caterpilla4076",  # user agent name
                         username="Icy_Caterpillar4076",  # your reddit username
                         password="Icy_Password4caterpillar4076",
                         grant_type='password')  # your reddit password

    return reddit


def get_subreddit(start: str, end: str, subreddit: str, *args, **kwargs):
    """
    Get data from a subreddit throught the API
    """

    # Define Default args
    limit = kwargs.get('limit', 100)
    query = kwargs.get('query', None)
    # Connect to PushshiftAPI
    reddit = access_reddit()
    api = PushshiftAPI(reddit)
    # Define Start End
    start = parser.parse(start)
    end = parser.parse(end)
    # Create Generator
    gen = api.search_submissions(
        subreddit=subreddit,
        q=query,
        after=start,
        before=end,
        limit=limit)

    # Columns of the DataFrame
    features = ['date', 'title', 'body', 'score', 'ups', 'downs',
                'upvote_ratio', 'num_comments', 'id', 'subreddit',
                'submission', 'redditor', 'url']

    # Collect Data in the DataFrame
    posts = []
    for post in gen:
        posts.append([
            post.created,
            post.title,
            post.selftext,
            post.score,
            post.ups,
            post.downs,
            post.upvote_ratio,
            post.num_comments,
            post.id,
            post.subreddit,
            post,
            post.author,
            post.url
        ])
    df = pd.DataFrame(posts, columns=features)
    df['date_parsed'] = df.date.apply(date_parser_utc)
    df['user'] = df.redditor.astype(str)

    return df


def get_comments(submissions):
    """
    Getting the comments from a submissions id list.
    """
    submissionList = []
    for s in submissions:
        s.comments.replace_more(limit=None)
        for comm in s.comments.list():
            try:
                submissionList.append(
                    [
                        comm.created,
                        comm.author.name,
                        comm.body,
                        comm.depth,
                        comm.score,
                        comm.ups,
                        comm.downs,
                        comm.author.id,
                        comm.parent_id,
                        comm.id,
                        comm.submission.id
                    ]
                )
            except AttributeError:
                pass

    comm_features = ['created', 'user', 'body',
                     'depth', 'score', 'ups', 'downs',
                     'author_id', 'parent_id', 'comment_id', 'submission_id']

    c = pd.DataFrame(submissionList, columns=comm_features)
    return c
