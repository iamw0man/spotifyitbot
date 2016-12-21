"""
Find top result from spotify with search term
and reply to posts with the keyword
SpotifyIt!
"""

import os
import sys
import time
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import spotipy
import praw
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_spotify_result(comment_text):
    """
    Query Spotify to return top result
    """
    print('getting spotify result...')
    sys.stdout.flush()
    try:
        query = comment_text.split('!', 1)

        spotify_response = SPOTIFY.search(q=query[1], limit=1)
        spotify_response = json.dumps(spotify_response)
        spotify_response = json.loads(spotify_response)

        spotify_response = spotify_response["tracks"]["items"]
        artist = [item["album"]["artists"][0]["name"] for item in spotify_response]
        track = [item["name"] for item in spotify_response]
        album = [item["album"]["name"] for item in spotify_response]
        url = [item["external_urls"]["spotify"] for item in spotify_response]

        top_result = 'Artist: {0} \n\nTrack: {1} \n\nAlbum: \
        {2} \n\nURL: {3}'.format(artist[0], track[0], album[0], url[0])

    except Exception as error:
        top_result = 'No results returned. \n\nPlease try again with different keywords.'
        print('[spotify] Error: {0}'.format(error))
        sys.stdout.flush()

    return top_result

def search_for_comments():
    """
    Request comments with KEYWORD
    """
    print('getting comment list...')
    sys.stdout.flush()
    try:
        request = requests.get(\
        'https://api.pushshift.io/reddit/search?q=%22SpotifyIt!%22&limit=100',\
        headers={'User-Agent':'SpotifyItBot-Agent'}, verify=False)
        pushshift_response = request.json()
        pushshift_response = pushshift_response["data"]
    except Exception as error:
        print('[pushshift] Error: {0}'.format(error))
        sys.stdout.flush()

    return pushshift_response

def main():
    """
    Check for duplicates and comment on new searches
    """
    while True:
        comments = search_for_comments()
        try:
            for com in comments:
                comment_text = com["body"]
                comment_id = com["id"]
                submission = REDDIT.comment(comment_id)
                if comment_id not in SPOTIFIED_POSTS:
                    reply = get_spotify_result(comment_text)
                    SPOTIFIED_POSTS.append(comment_id)
                    disclaimer = "I'm a bot bleep bloop. \
                    \n\nPM me for more information or to report any issues."
                    submission.reply('{0}\n\n\n{1}'.format(reply, disclaimer))
                    print('Replied to {0} \n{1}'.format(comment_id, reply))
                    sys.stdout.flush()
                    print('writing to file...')
                    sys.stdout.flush()
                    # write to file
                    with open("SPOTIFIED_POSTS.txt", "w") as text_file:
                        for comment_id in SPOTIFIED_POSTS:
                            text_file.write(comment_id + "\n")
        except Exception as error:
            print('[main] Error: {0}'.format(error))
            sys.stdout.flush()
        time.sleep(60)

# runner
print("start...")
sys.stdout.flush()

REDDIT = praw.Reddit('spotify_it_bot')
SPOTIFY = spotipy.Spotify()
SUB = REDDIT.subreddit('all')
KEYWORD = 'SpotifyIt!'

# create file to record replies
if not os.path.isfile("SPOTIFIED_POSTS.txt"):
    SPOTIFIED_POSTS = []
else:
    with open("SPOTIFIED_POSTS.txt", "r") as f:
        SPOTIFIED_POSTS = f.read()
        SPOTIFIED_POSTS = SPOTIFIED_POSTS.split("\n")
        SPOTIFIED_POSTS = list(filter(None, SPOTIFIED_POSTS))

main()
