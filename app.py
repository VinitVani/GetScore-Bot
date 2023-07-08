from flask import Flask, request
import requests
import json
import re

app = Flask(__name__)
# env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
# app.config.from_object(env_config)

API_KEY = "cb2eabb7-28a1-4d64-9904-4057522e0d84"


WEBHOOK_URL = "/ https://0c2a-49-43-41-134.ngrok.io"

test_nations = list(
    ["Australia", "England", "South Africa", "West Indies", "New Zealand", "India", "Pakistan", "Sri Lanka", "Zimbabwe",
     "Bangladesh", "Ireland", "Afghanistan"])
ipl_teams = list(
    ["Chennai Super Kings", "Delhi Capitals", "Gujarat Titans", "Kolkata Knight Riders", "Lucknow Super Giants",
     "Mumbai Indians", "Punjab Kings", "Rajasthan Royals", "Royal Challengers Bangalore", "Sunrisers Hyderabad"])
wpl_teams = list(["Mumbai Indians Women", "Delhi Capitals Women", "Gujarat Giants", "UP Warriorz",
                  "Royal Challengers Bangalore Women"])


def get_test_score(n, no_of_innings, data):
    final = ""
    for i in range(0, no_of_innings):
        inning1 = data["data"][n]["score"][i]['inning']
        runs1 = data["data"][n]["score"][i]['r']
        wkts1 = data["data"][n]["score"][i]['w']
        overs1 = data["data"][n]["score"][i]['o']
        result = "In " + inning1[-9:-1] + str(i + 1) + " " + inning1[0:-9] + " scores " + str(
            runs1) + " runs in " + str(overs1) + " overs with the loss of " + str(
            wkts1) + " wickets. \n"
        final += result
        return final


def getScore(n, data):
    inning1 = data["data"][n]["score"][0]['inning']
    runs1 = data["data"][n]["score"][0]['r']
    wkts1 = data["data"][n]["score"][0]['w']
    overs1 = data["data"][n]["score"][0]['o']

    if len(data["data"][n]["score"]) >= 2:
        inning2 = data["data"][n]["score"][1]['inning']
        runs2 = data["data"][n]["score"][1]['r']
        wkts2 = data["data"][n]["score"][1]['w']
        overs2 = data["data"][n]["score"][1]['o']

        result = inning1[0:-9] + " scores " + str(runs1) + " runs in " + str(overs1) + " overs with the loss of " + str(
            wkts1) + " wickets while " + inning2[0:-9] + " scores " + str(runs2) + " runs in " + str(
            overs2) + " overs with the loss of " + str(wkts2) + " wickets. Current Status of match is : " + \
                 data["data"][n]["status"]
    else:
        result = inning1[0:-9] + " scores " + str(runs1) + " runs in " + str(overs1) + " overs with the loss of " + str(
            wkts1) + " wickets. Secound Inning is yet to start."

    return result


def getdata(t1, t2):
    url = "https://api.cricapi.com/v1/currentMatches?apikey=cb2eabb7-28a1-4d64-9904-4057522e0d84&offset=0"

    response = requests.request("GET", url)
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()
        for i in range(0, len(data['data'])):
            match_name = data['data'][i]['name']
            list_from_name = [x.strip() for x in re.split("vs|,", match_name)]

            if t1 and t2 in list_from_name:
                if "Test" in list_from_name[2]:
                    no_of_innings = len(data["data"][i]["score"])
                    score = get_test_score(i, no_of_innings, data)

                    return score

                score = getScore(i, data)
                return score


    else:
        # Handle errors
        print("Request failed: ", response.status_code)


@app.route("/", methods=['POST'])
def webhook():
    # Get JSON data from request
    req = request.get_json()

    # Get intent name from request
    intent = req['queryResult']['intent']['displayName']

    # Handle get_score intent
    if intent == 'Score':
        # Get team names from entities
        team1 = req['queryResult']['parameters']['Team1']
        team2 = req['queryResult']['parameters']['Team2']
        score = getdata(team1, team2)

        res = {
            "fulfillmentText": score,
            "source": "webhook"
        }
        return json.dumps(res)
        return "Hello"
    else:
        # Handle other intents or default fallback
        return {}


if __name__ == '__main__':
    app.run(debug=False,port ='0.0.0.0')
