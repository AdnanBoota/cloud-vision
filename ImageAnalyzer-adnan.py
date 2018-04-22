#!/usr/bin/env python
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script uses the Vision API's label detection capabilities to find a label
based on an image's content.

To run the example, install the necessary libraries by running:

    pip install -r requirements.txt

Run the script on an image to get a label, E.g.:

    ./label.py <path-to-image>
"""

# [START import_libraries]
import argparse
import base64

import googleapiclient.discovery

import tweepy
from tweepy import OAuthHandler
import json
import wget
import os
from PIL import Image
import glob
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np

# [END import_libraries]

csvData = []

# receive profile url, get 100 images url
# for each url, send that image to the google cloud vision, and receive tags
# store tags and probabilities for each image in a text file
# create a png file from those text file

def googleCloudVision():
    """Run a label request on a single image"""

    # [START authenticate]
    service = googleapiclient.discovery.build('vision', 'v1')
    # [END authenticate]

    # [START construct_request]
    for media_file in image_list:
        with open(media_file, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    'features': [{
                        'type': 'LABEL_DETECTION',
                        'maxResults': 5
                    }]
                }]
            })
            # [END construct_request]
            # [START parse_response]
            response = service_request.execute()
            saveCsvFile(response, media_file)


def getTweetImages(username):
    tweets = api.user_timeline(screen_name=username,
                               count=tweets_count, include_rts=False,
                               exclude_replies=True)
    last_id = tweets[-1].id

    while (True):
        more_tweets = api.user_timeline(screen_name=username,
                                        count=tweets_count,
                                        include_rts=False,
                                        exclude_replies=True,
                                        max_id=last_id - 1)
        # There are no more tweets
        if (len(more_tweets) == 0):
            break
        else:
            last_id = more_tweets[-1].id - 1
            tweets = tweets + more_tweets

    for status in tweets:
        media = status.entities.get('media', [])
        if (len(media) > 0 and len(images_files) <= images_count):
            images_files.add(media[0]['media_url'])

    print(images_files)

    for media_file in images_files:
        wget.download(media_file, out='twitter_images/')

    for filename in glob.glob('twitter_images/*'):
        # im = Image.open(filename)
        image_list.append(filename)


def saveCsvFile(response, media_file):
    print("Results for image %s:" % media_file)
    for result in response['responses'][0]['labelAnnotations']:
        csvData.append([media_file.replace('twitter_images/', ''), result['description'], result['score']])
        print("%s - %.3f" % (result['description'], result['score']))
    # [END parse_response]

    myFile = open('score.csv', 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(csvData)


def plotChart():
    x_axis = []
    y_axis = []
    with open('score.csv') as File:
        reader = csv.reader(File, delimiter=',', quotechar=',',
                            quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            print(row[1] + ' - ' + row[2])
            x_axis.append(row[1])
            y_axis.append(row[2])

        plt.bar(range(len(x_axis)), y_axis, width=0.75, align='center')
        plt.xticks(range(len(x_axis)), x_axis, rotation=60)
        plt.axis('tight')
        plt.show()  # show it on IDE
        plt.savefig('plots/barPlot.png')  # save it on a file


@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status




# ************************************************************************
# ********************* Twitter Authentication ***************************
# ************************************************************************

# consumer_key = os.environ.get('TWITTER_CONS_KEY')
# consumer_secret = os.environ.get('TWITTER_CONS_SECRET')
# access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
# access_secret = os.environ.get('TWITTER_ACCESS_SECRET')

consumer_key = 'VJszSPvP8IFWIKtdNskq52leQ'
consumer_secret = 'eNK7w8juR2MiYqRAy7YxFHNUCVoaHsvWOhcgoMh6XivyRwGDHh'
access_token = '4021413983-kQOrLRK0jpWw7V5RshKuMiFbTIo3yd67YKv4i1L'
access_secret = 'l6tJlwLynjtQYNUX31eS4QqenW2a1tSPg189RoMGi61cX'

# Status() is the data model for a tweet
tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse
# User() is the data model for a user profil
tweepy.models.User.first_parse = tweepy.models.User.parse
tweepy.models.User.parse = parse
# You need to do it for all the models you need

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)


# ************************************************************************
# ************************ Main Application ******************************
# ************************************************************************

images_files = set()
image_list = []

tweets_count = 100
images_count = 100



# [START run_application]
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='The username you\'d like to get tweet images.')
    args = parser.parse_args()

    username = args.username
    # get images from the tweets given a username
    getTweetImages(username)
    # get tags and probablity from google cloud vision api and save it to the csv file
    googleCloudVision()
    # plot chart from csv file data
    plotChart()
# [END run_application]
