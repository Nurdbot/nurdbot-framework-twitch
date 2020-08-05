def TOGGLE_OPS_RESPONSE_0():
    response = f'Operator state configured to addop only.'
    return response

def TOGGLE_OPS_RESPONSE_1(nick):
    response = f'All VIPs and Moderators are now {nick} operators.'
    return response

def TOGGLE_MUTE_MUTED(nick):
    response =f'{nick} is now muted.'
    return response

def TOGGLE_MUTE_UNMUTE(nick):
    response = f'{nick} is now unmuted.'
    return response

def INVALID_PERMISSIONS_MESSAGE(username):
    response = f'You do not have the authorty to use that command, {username}'
    return response

def OPERATOR_ADD_MESSAGE(username):
    response = f'{username} successfully added as an operator.'
    return response

def OPERATOR_REMOVE_MESSAGE(username):
    response = f'{username} successfully removed as an operator.'
    return response

def RAFFLE_CLOSED_MESSAGE():
    response = "< RAFFLE IS NOW CLOSED >"
    return response

def RAFFLE_START_MESSAGE(keyword):
    response = f'< RAFFLE STARTED, TYPE THE KEYWORD {keyword} ONCE TO ENTER >'
    return response

def SHOUTOUT_MESSAGE(target):
    response = f'Hey be sure to check out https://twitch.tv/{target}'
    return response