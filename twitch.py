import string, random, socket, os, time, requests, sqlite3
from os import path
from datetime import datetime
from config import *
from output import *

channel = f'#{user}'
channel_owner = user
#this can be any path you'd like. By default we're going to use 
database_file = f'database/{user}.db'

#make a bunch of empty lists so that python doesnt freak out.
operators = []
commands = []

#find right now
now = datetime.now()

keyword = reset_keyword

"""
DO A BUNCH OF DATABASE SCIENCE
"""

def create_database():
    with open (database_file, "a") as database:
        database.write("")
    print("database created")

def init_logs():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS logs (time TEXT, username TEXT NOT NULL, message TEXT )') 
    connection.commit()
    connection.close()
    print("logs initiated.")

def init_operators():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS operators (username TEXT NOT NULL)')
    connection.commit()
    connection.close()
    print('operators initiated')

def init_commands():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS commands (keyword TEXT NOT NULL UNIQUE, output TEXT NOT NULL) ')
    connection.commit()
    connection.close()
    print('commands initiated')


def init_configurable():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS configurable (alias TEXT NOT NULL, value INTEGER )') 
    connection.commit()
    #check for raffle state
    raffle_state = cursor.execute("select * from configurable where alias = 'raffle_state'").fetchone()
    if raffle_state:
        print('raffle state found')
    else:
        cursor.execute("insert into configurable (alias, value) values ('raffle_state', 0)")
        connection.commit()
    #check for operator state
    operator_state = cursor.execute("select * from configurable where alias = 'operator_state'").fetchone()
    if operator_state:
        print('operator_state state found')
    else:
        cursor.execute("insert into configurable (alias, value) values ('operator_state', 0)")
        connection.commit()
    #check for mute state
    mute_state = cursor.execute("select * from configurable where alias = 'mute_state'").fetchone()
    if mute_state:
        print('operator_state state found')
    else:
        cursor.execute("insert into configurable (alias, value) values ('mute_state', 0)")
        connection.commit()
    connection.close()
    print("configurable initiated")


def init_database():
    init_logs()
    init_operators()
    init_commands()
    init_configurable()


if path.exists(database_file):
    print("found db, continuting")
    init_database()
else:
    print("didn't find db, making one")
    create_database()
    init_database()


"""
ACTUALLY DO BOT THINGS
"""

s = socket.socket()
s.connect((host, port))
s.send(bytes("PASS " + password + "\r\n", "UTF-8"))
s.send(bytes("NICK " + nick + "\r\n", "UTF-8"))
s.send(bytes("JOIN " + channel + "\r\n", "UTF-8"))


def log_message(username, message):
    if nick+".tmi.twitch.tv" in username:
        print(message)
    elif "tmi.twitch.tv 421 "+nick+" PONG" in username:
        print(message)
    else:
        print(username)
        stamp = now.strftime("%m/%d/%Y %H:%M:%S")
        connection = sqlite3.connect(database_file)
        cursor = connection.cursor()
        cursor.execute("insert into logs (time, username, message) values (?, ?, ?)",(stamp, username, str(message)))
        connection.commit()
        connection.close()

def add_clip(output):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute("insert into responses (tag, output) values (?, ?)", ("!clip",output))
    connection.commit()
    connection.close()

def add_operator(user):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute("insert into operators (username) values (?)",(user,))
    connection.commit()
    connection.close()
    operators.append(user)
    print('added '+user+' to operators')

def remove_operator(user):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute("delete from operators where username = ?",(user,))
    connection.commit()
    connection.close()
    print('removed '+user+' from operators')

def add_command(keyword, output):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute("insert into commands (keyword, output) values (?, ?)",(keyword, output))
    connection.commit()
    connection.close()
    print('added '+keyword+' command to commands')

def get_follow_age(user):
    url = 'https://api.2g.be/twitch/followage/'+channel_owner+'/'+user+'?format=mwdhms'
    response = requests.get(url)
    data = response.text
    return str(data)

def get_uptime():
    url = 'https://beta.decapi.me/twitch/uptime/'+channel_owner
    response = requests.get(url)
    data = response.text
    return str(data)

def get_insult():
    url ='https://insult.mattbas.org/api/insult'
    response = requests.get(url)
    data = response.text
    return str(data)

def get_compliment():
    url ='https://complimentr.com/api'
    response = requests.get(url)
    data = response.json()
    return str(data['compliment'])

def get_raffle_state():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    raffle_state = cursor.execute("select * from configurable where alias ='raffle_state'").fetchone()
    if raffle_state[1] == 1:
        return raffle_state[1]
    else:
        keyword = reset_keyword

def raffle(state, keyword):
    if state =='active':
        connection = sqlite3.connect(database_file)
        cursor = connection.cursor()
        cursor.execute("update configurable set value =? where alias ='raffle_state'",(1,))
        connection.commit()
        connection.close()
        keyword = keyword
        clear = open("scratch/"+channel_owner+".txt", "w")
        clear.close()
    else:
        connection = sqlite3.connect(database_file)
        cursor = connection.cursor()
        cursor.execute("update configurable set value =? where alias ='raffle_state'",(0,))
        connection.commit()
        connection.close()
        keyword = reset_keyword
        #set state to inactive
        #set keyword to whatever was in config

def add_participant(username):
    with open("scratch/"+channel_owner+".txt", "a+") as raffle_file:
        check = open("scratch/"+channel_owner+".txt", "r")
        if username in check.read():
            print('found the bro did nothing')
            check.close()
        else:
            raffle_file.write(username+'\r\n') 

def get_winner():
    raffle('closed', 'keyword')
    lines = open("scratch/"+channel_owner+".txt").read().splitlines()
    if lines:
        winner = random.choice(lines)
        return winner
    else:
        return "no one entered the raffle :("


def find_more_operators():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    operator_state = cursor.execute("select * from configurable where alias ='operator_state'").fetchone()
    if operator_state[1] == 1:
        url = 'https://tmi.twitch.tv/group/user/'+channel_owner+'/chatters'
        response = requests.get(url)
        data = response.json()
        ops =[]
        for vip in data['chatters']['vips']:
            ops.append(vip)
        for moderator in data['chatters']['moderators']:
            ops.append(moderator)
    else:
        ops=[]
    more_ops = cursor.execute('select * from operators').fetchall()
    connection.close()
    for user in more_ops:
        ops.append(user[0])
    return ops

def output_command(keyword):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    command = cursor.execute('select * from commands where keyword = ?', (keyword,)).fetchone()
    #!HERE SPEED - consider just fixing the sql.
    mute_state = get_configurable_value("mute_state")
    if mute_state == 0:
        if "<ARRAY>" in command[1]:
            outputs = cursor.execute('select * from responses where tag = ?', (keyword,)).fetchall()
            connection.close()
            #print(output)
            responses=[]
            for output in outputs:
                responses.append(output[1])
            if "!clip" in command[0]:
                send_message(str("https://"+random.choice(responses)))
            else:
                send_message(str(random.choice(responses)))
        else:
            connection.close()
            send_message(command[1])

def find_commands():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    keywords = cursor.execute('select * from commands').fetchall()
    connection.close()
    commands =[]
    for keyword in keywords:
        commands.append(keyword[0])
    return commands

def reload_commands():
    commands =[]
    commands.extend(find_commands())
    return commands

def reload_operators():
    operators =[]
    operators.extend(admins)
    operators.extend(find_more_operators())
    return operators

def toggle_operator():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    state =cursor.execute ("select * from configurable where alias = 'operator_state'").fetchone()
    if state[1] ==1:
        cursor.execute("update configurable set value = 0 where alias ='operator_state'")
        connection.commit()
        send_message(TOGGLE_OPS_RESPONSE_0())
    else:
        cursor.execute("update configurable set value = 1 where alias ='operator_state'")
        connection.commit()
        send_message(TOGGLE_OPS_RESPONSE_1(nick))
    connection.close()

def toggle_mute():
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    state =cursor.execute ("select * from configurable where alias = 'mute_state'").fetchone()
    if state[1] ==1:
        cursor.execute("update configurable set value = 0 where alias ='mute_state'")
        connection.commit()
        send_message(TOGGLE_MUTE_UNMUTE(nick))
    else:
        cursor.execute("update configurable set value = 1 where alias ='mute_state'")
        connection.commit()
        s.send(bytes("PRIVMSG "+channel+" :"+TOGGLE_MUTE_MUTED(nick)+"\r\n", "UTF-8"))

    connection.close()


def set_configurable_value(value, alias):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute("update configurable set value =? where alias =?",(value, alias))
    connection.commit()
    connection.close()

def get_configurable_value(alias):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    value = cursor.execute("select * from configurable where alias =?",(alias, )).fetchone()
    connection.close()
    return int(value[1])

def send_message(message):
    log_message(nick, message)
    print(nick+": "+message)
    mute_state = get_configurable_value("mute_state")
    if mute_state == 0:
        s.send(bytes("PRIVMSG "+channel+" :"+message+"\r\n", "UTF-8"))

def send_whisper(user, message):
    log_message(nick+" - Whisper", message)
    print(nick+" whispers: "+message)
    mute_state = get_configurable_value("mute_state")
    if mute_state == 0:
        s.send(bytes("PRIVMSG "+channel+" :/w "+user+" "+message+"\r\n", "UTF-8"))

while True:
    get_raffle_state()
    line = str(s.recv(1024))
    if "End of /NAMES list" in line:
        break

    while True:
        for line in str(s.recv(1024)).split('\\r\\n'):

            del operators
            operators = reload_operators()
            print("operators are "+str(operators))
            del commands
            commands = reload_commands()

             #defeat twitch idle prevention    
            if line.find('PING') != -1:
                print(line)
                s.send(bytes("PONG"+line.split()[1]+"r\n", "UTF-8"))
                print("SENT PONG")
            
            parts = line.split(':')
            if len(parts) < 3:
                continue
            
             #escape or load user names. because twitch chat.
            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                message = parts[2][:len(parts[2])]
                message_ci = message.lower()
                usernamesplit = parts[1].split("!")
                username = usernamesplit[0]
                print(username + ": " + str(message))
                log_message(username, message)
                #probably !HERE !FIX  message.startswith()?
            if line.find('!addclip https') !=-1:
                if username in operators:
                    clip = line.split('https://')
                    add_clip(str(clip[1]))
                    send_message(CLIP_SUCCESS_MESSAGE(username))
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))

            for command in commands:
                if message_ci.startswith(command):
                    output_command(str(command))

            #message = caseSensitiveMessage
            #message_ci = caseinsentiviemessage

            if  message.startswith("!addcommand"):
                if username in operators:
                    command_keyword = message.split(" ")
                    #this escapes after the colon in message should look at line
                    command = message.split(command_keyword[1])
                    if line.find('https') !=-1:
                        text_body = line.split('https://')
                        actual_output = command[1]+ str(text_body[1])
                        fixed_output = actual_output.replace('https', ' https://')
                        add_command(command_keyword[1], fixed_output)
                    else:
                        add_command(command_keyword[1], command[1])
                    del commands
                    commands = reload_commands()
            
            if message_ci =='!followage':
                send_message(str(get_follow_age(username)))

            if message_ci == '!uptime':
                send_message("Current uptime for "+channel_owner+" is "+get_uptime())

            if message_ci =='!insult':
                send_message(get_insult() +" "+username)
            
            if message_ci =='!compliment':
                send_message(get_compliment() +" "+username)

            if message.startswith("!shoutout") or  message.startswith("!so"):
                if username in operators:
                    user = message.split(" ")
                    send_message(SHOUTOUT_MESSAGE(user[1]))
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))
            
            if message_ci =='!togglemute':
                if username in operators:
                    toggle_mute()
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))
            
            if message_ci =='!toggleops':
                if username in operators:
                    toggle_operator()
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))
                
            
            if message.startswith('!addop'):
                if username in operators:
                    target = str(message.split("!addop")[1].strip().lower())
                    add_operator(target)
                    send_message(OPERATOR_ADD_MESSAGE(target))
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))
                
            if message.startswith('!rmop'):
                if username in operators:
                    target = str(message.split("!rmop")[1].strip().lower())
                    remove_operator(target)
                    send_message(OPERATOR_REMOVE_MESSAGE(target))
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))

            if keyword in message:
                print('found' +keyword)
                if get_raffle_state() ==1:
                    add_participant(username)
            
            if message.startswith("!raffle"):
                if username in operators:
                    parse = message.split(" ")
                    if len(parse) < 2: #courtesy of M3talstorm
                        send_message(INVALID_KEYWORD_MESSAGE(username))
                    else:
                        keyword = parse[1].strip()
                        raffle('active', keyword)
                        send_message(RAFFLE_START_MESSAGE(keyword))    
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))
            
            if message == '!draw':
                if username in operators:
                    send_message(RAFFLE_CLOSED_MESSAGE())
                    time.sleep(1.2)
                    send_message("3")
                    time.sleep(1.2)
                    send_message("2")
                    time.sleep(1.2)
                    send_message("1")
                    time.sleep(1.2)
                    send_message(get_winner())
                else:
                    send_message(INVALID_PERMISSIONS_MESSAGE(username))

             #escape loop to allow for repeated commands
            if username == nick:
                pass