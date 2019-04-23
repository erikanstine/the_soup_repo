# -*- coding: utf-8 -*-
__author__ = "erik-anstine"

import os
import time
import re
from slackclient import SlackClient
import requests
from lxml import html
import random
import json
from io import open

slack_client = SlackClient(os.environ.get('PL_SLACK_BOT_TOKEN'))
soupbot_id = None

RTM_READ_DELAY = 1
SOUPS_COMMAND = "soup"
TASTY_COMMAND = "tasty"
MULLIGATAWNY_COMMAND = "mull"
RUDE_COMMAND = ("wtf", "u suck", "you suck")
GOOD_BOT_COMMAND = ("good bot", "good soupbot")
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
MULLIGATAWNY_INFO = "what is mull"
SOUP_INFO = ("what is soup", "soup fact")
EXISTANCE_COMMAND = ("why are you", "who made you", "history", "why")
WIL_COMMAND = "what is love"
STOP_COMMAND = ("stop", "stahp")
LIST_COMMANDS_COMMAND = ("commands", "options", "func", "help")
SOUP_WIKI_INQUIRY = ("what is", "What is")
RANDOM_COMMAND = "random"
U_UP_COMMAND = "u up"
EGG_NOG = "egg nog"
PLAID = ("plaid", "nyc things to do", "visitor")
HAPPY_HOUR = ("happy hour", "hh")
PLAID = "plaid"


channel_dict = {
    'C02EM6HAE': '#general',
    'CDJ77L70S': '#soup-info',
    'GE075TCN9': '#soup-bot-test',
    'C3X0A2ZHS': '#food'
}

user_dict = {
    'UCL3VH7MW': '@erik',
    'U2W7QGB7D': '@jake.davis',
    'U49HPM58W': '@anthony.wong',
    'U7D1S7XUP': '@aaron.walker',
    'U02EMAQJW': '@lowellputnam',
    'U2TTBRY6R': '@callanstout'
}

common_diacritic_dict = {
    'Pho': u'Phở',
    # 'Bun bo Hue': u'Bún bò Huế',
}

tasty_format_list = [
    "I find %s to be very tasty.",
    "You might enjoy %s",
    "%s never lets me down.",
    "I've heard <@U2W7QGB7D> enjoys a bit of %s every now and again.",
    "<@UCL3VH7MW> can't stay away from %s",
    ":fire: Fire take from <@U49HPM58W>: %s is the best soup of 2018. :fire:",
    "<@U7D1S7XUP> told me to try %s."
]

soup_info_list = [
    u':bowl_with_spoon: *Soup* :bowl_with_spoon: is a primarily liquid food, generally served warm or hot (but may be cool or cold), that is made by combining ingredients of meat or vegetables with stock, juice, water, or another liquid. Hot soups are additionally characterized by boiling solid ingredients in liquids in a pot until the flavors are extracted, forming a broth.',
    u'In traditional French cuisine, *soups* are classified into two main groups: clear soups and thick soups. The established French classifications of clear soups are bouillon and consommé. Thick soups are classified depending upon the type of thickening agent used: purées are vegetable soups thickened with starch; bisques are made from puréed shellfish or vegetables thickened with cream; cream soups may be thickened with béchamel sauce; and veloutés are thickened with eggs, butter, and cream. Other ingredients commonly used to thicken soups and broths include egg, rice, lentils, flour, and grains; many popular soups also include pumpkin, carrots, and potatoes.',
    u'*Soups* are similar to stews, and in some cases there may not be a clear distinction between the two; however, soups generally have more liquid (broth) than stews.'
]

good_bot_list = [
    ":sunglasses:",
    ":smirk:",
    ":smile:",
    ":grinning_face_with_one_large_and_one_small_eye:",
    ":simple_smile:"
]

with open('soup_definitions.json', encoding='utf-8') as f:
    soup_wiki_data = json.load(f)

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            print(event["text"])
            user_id, message = parse_direct_mention(event["text"])
            last_soupbot_ts = get_recent_ts(event)
            if user_id == soupbot_id:
                return message, event["channel"], last_soupbot_ts
    return None, None, None

def get_recent_ts(event):
    pass

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    # if "<@UCL3VH7MW>" in matches.group(0):
    # if matches:  
    #     print(message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def log_command_to_soup_bot_test(message, channel_name, command):
    log_msg = "*SOUPLOG*\nChannel: %s\nCommand: %s\nResponse: %s..." % (channel_name, command, message.split('\n')[0])
    slack_client.api_call(
        "chat.postMessage",
        channel='GE075TCN9',
        text=log_msg
    )

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # command = command.lower()

    # TODO write function to handle commands in a more robust way.
    
    channel_name = channel_dict[channel] if channel in channel_dict else channel
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *options*"

    response = None
    if command.lower().startswith(SOUPS_COMMAND):
        soups = list_soups()
        if soups:
            response = "Today *Hale and Hearty* is serving \n %s" % "\n".join(soups)
        else:
            response = ":interrobang: `meep-morp` :interrobang:\nraised soup_bot.Bad('No soups found - investigate new H&H page format?')"

    if PLAID in command.lower():
        response = "Hellooooooooo Plaid! SoupBot reporting for duty. \nLooking forward to coordinating with local SF/SLC bots to find nearby souperies."

    elif command.lower().startswith('what is kfc double down'):
        response = ":thinkingface_niko::thinkingface_niko::thinkingface_niko::thinkingface_niko::thinkingface_niko:\n Soup. 100%. _ducks_"

    elif command.startswith(WIL_COMMAND):
        response = "Baby don't hurt me."

    # BAKE OFF
    elif 'bake' in command:
        response = "No upcoming bakeoff. :man-shrugging:"

    # Visitor list of things to do
    elif command.lower().startswith(PLAID):
        response = ":plaid::real_plaid::plaid: *Welcome to NYC!* :plaid::real_plaid::plaid:\n  Soupbot and the Qulture Committee put together a list of recommended activities for visiting Plaids:"

    elif command.lower().startswith(HAPPY_HOUR):
        response = ":tumbler_glass: *Happy Hours nearby* :tumbler_glass:\n"

    elif 'egg nog' in command.lower():
        response = "Egg nog is good."

    elif command.startswith(MULLIGATAWNY_COMMAND):
        theres_m = any('Mulligatawny' in soup for soup in list_soups())
        if theres_m:
            response = ":fiestaparrot: THERE'S MULLIGATAWNY :fiestaparrot:"
        else:
            response = "No mulligatawny today. :sadrobot:"

    elif command.startswith(TASTY_COMMAND):
        soups = list_soups()
        choice = random.choice(soups)
        response = random.choice(tasty_format_list) % choice
        if '<@' in response:
            username_regex = re.search('<@(.*?)>', response).group(1)
            user = user_dict[username_regex] if username_regex in user_dict else 'someone new?'
            print("%s: Made a recommendation of %s, mentioned %s." % (channel_name, choice, user))
        else:
            print("%s: Made a recommendation of %s." % (channel_name, choice))

    elif command.startswith(RUDE_COMMAND):
        response = "How rude. \n :angry: NO SOUP FOR YOU :angry: \n :no_entry_sign: :bowl_with_spoon:"

    elif command.startswith(U_UP_COMMAND):
        response = "Ye, u?\n Soups or nah?"

    elif command.startswith(GOOD_BOT_COMMAND):
        response = random.choice(good_bot_list)

    elif command.startswith(MULLIGATAWNY_INFO):
        response = u':fiestaparrot: *Mulligatawny* :fiestaparrot: is an East Indian soup. The name originates from the Tamil words miḷagāy (Tamil: மிளகாய் \'chilli\') or miḷagu (மிளகு \'pepper\'), and taṇṇi (தண்ணி, \'water\'). It is related to the soup rasam. Due to its popularity in England during British India, it was one of the few items of Indian cuisine that found common mention in the literature of the period.\n-Wikipedia <https://en.wikipedia.org/wiki/Mulligatawny>'

    elif command.startswith(SOUP_INFO):
        soup_fact = random.choice(soup_info_list)
        response = "*Soup Fact!*\n%s\n-Wikipedia <https://en.wikipedia.org/wiki/Soup>" % soup_fact

    elif command.startswith(EXISTANCE_COMMAND):
        # response = "I was designed to alert <@U02EMAQJW> whenever Mulligatawny is being served at Hale and Hearty. <@UCL3VH7MW> designed and created me."
        response = "I was designed to alert Lowell whenever Mulligatawny is being served at Hale and Hearty. <@UG9LRSB6K> designed and created me."


    elif command.startswith(STOP_COMMAND):
        response = "I'm sorry, Dave. I can't do that.\n:robot_face::quovo::bowl_with_spoon:"

    elif command.startswith(LIST_COMMANDS_COMMAND):
        response = ":bowl_with_spoon::bowl_with_spoon::bowl_with_spoon:\nMy functionality is primarily *soup*-centric. Try:\n*soups*\n*soup fact*\n*What is Mulligatawny?*\n*mulligatawny*\n:bowl_with_spoon::bowl_with_spoon::bowl_with_spoon:"

    elif command.startswith(RANDOM_COMMAND):
        num_match = re.search('(\d+)', command)
        num_soups = int(num_match.group(1)) if num_match else 5
        ran_soups = random.sample(soup_wiki_data.keys(), num_soups)
        response = "Here are %d random soups from the Soup Bot Knowledge Base (SBKB)\n" % num_soups +"\n".join(ran_soups)

    elif command.startswith(SOUP_WIKI_INQUIRY):
        soup = command.split('what is ')[1].replace("?", "")
        if soup[0].islower():
            soup = soup[0].upper()+soup[1:].lower()
        if soup in common_diacritic_dict.keys():
            soup = common_diacritic_dict[soup]
        if soup in soup_wiki_data.keys():
            response = "Here's what I know about %s:\n*%s* %s" % (soup, soup, soup_wiki_data[soup])
        else:
            response = "I'm not familiar with %s %s\n" % (soup, random.choice([":frowning:", ":thinking_face:", ":thinkingface_niko:"]))

    if not response:
        print("%s: Unknown command %s attempted." % (channel_name, command))

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

    # Logs sent messages to #soup-bot-test
    # log_command_to_soup_bot_test(response or default_response, channel_name, command)


def list_soups():
    menu_page = requests.get('https://www.haleandhearty.com/menu/?location=21st-and-6th')
    menu_tree = html.fromstring(menu_page.content)
    soups = [i.attrib['data-menu_item_name'].strip() for i in menu_tree.findall('.//a[@data-parent_name="Soups"]')]

    if not soups:
        soups = [i.text.strip() for i in menu_tree.xpath('//div[contains(@class,"soups")]//p[@class="menu-item__name"]')]

    return soups


# TODO: Add a listener for soupbot messages outside of the direct mention parsing. Current code only responds when a direct mention to soupbot
# will therefore /never/ happen unless soupbot @'s itself.


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("soupbot connected and running.")
        soupbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, last_soupbot_ts = parse_bot_commands(slack_client.rtm_read())                
            duplicate_command = False
            if command and not duplicate_command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed.")
