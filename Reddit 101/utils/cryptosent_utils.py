import praw

def get_reddit():
    reddit = praw.Reddit(client_id="f0b33JSRVGyB8p-ua4_58g",#my client id
                        client_secret="H6vEPyKbzDASg9G5hlAi7WoKdAE58g",  #your client secret
                        user_agent="Scraping Script 101 by u/Icy_Caterpilla4076", #user agent name
                        username = "Icy_Caterpillar4076",     # your reddit username
                        password = "Icy_Password4caterpillar4076",
                        grant_type = 'password')     # your reddit password

    return reddit
                        