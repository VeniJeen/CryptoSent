import praw
from psaw import PushshiftAPI
from dateutil import parser
import datetime as dt
import pandas as pd
from update_checker import UpdateResult



def date_parser(x):return dt.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')

def access_reddit():
    reddit = praw.Reddit(client_id="f0b33JSRVGyB8p-ua4_58g",#my client id
                        client_secret="H6vEPyKbzDASg9G5hlAi7WoKdAE58g",  #your client secret
                        user_agent="Scraping Script 101 by u/Icy_Caterpilla4076", #user agent name
                        username = "Icy_Caterpillar4076",     # your reddit username
                        password = "Icy_Password4caterpillar4076",
                        grant_type = 'password')     # your reddit password

    return reddit
                        

def get_subreddit(start:str, end:str, subreddit:str,*args, **kwargs):
    """
    Get data from a subreddit
    """

    #Define Default args
    limit = kwargs.get('limit', 100)
    query = kwargs.get('query', None)
    #Connect to PushshiftAPI 
    reddit = access_reddit()
    api = PushshiftAPI(reddit)
    #Define Start End
    start=parser.parse(start)
    end=parser.parse(end)
    #Create Generator
    gen=api.search_submissions(
                            subreddit=subreddit,
                            q=query,
                            after=start,
                            before=end,
                            limit=limit)

    #Columns of the DataFrame
    features=['date','title','body', 'score','ups','downs',
              'upvote_ratio','num_comments', 'id', 'subreddit', 
              'submission','redditor','url']

    #Collect Data in the DataFrame
    posts=[]
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
    df = pd.DataFrame(posts,columns=features)
    df['date_parsed']=df.date.apply(date_parser)
    df['user']=df.redditor.astype(str)

    return df




def get_comments(submissions):
    """
    submissions: reddit.submission object list
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
        

    comm_features=['created','user','body',
           'depth','score','ups','downs',
           'author_id','parent_id','comment_id','submission_id']

    c=pd.DataFrame(submissionList,columns=comm_features)
    return c

    