# nurdbot-framework-twitch
an example repo for how to implement several of nurdbots features in your own bot!

Do whatever you want with this, we're not really going to offer support or PRs. You can come hangout at https://twitch.tv/pronerd_jay to ask questions, no promises. Have fun! 

If you would like the fully featured nurdbot in your channel, pop over to https://twitch.tv/pronerd_jay and ask in chat! 


## setup instructions
rename sample-config.py to config.py
edit config.py to reflect reality, replacing placeholder data.

```sh
python3 -m venv env
```

```sh
source env/bin/activate
pip3 install -r req.txt
```
```sh
python3 twitch.py
```

## builtins
```!toggleops``` behaves as expected

```!togglemute``` behaves as expected

```!raffle KEYWORD``` will init a raffle using KEYWORD, participants can only enter once.

```!draw``` will close the raffle and select a winner, you can draw multiple times.


## customization
```!addcommand !command output```
is likely the best way to add custom commands. example ```!addcommand !discord https://discord.gg/butts``` will make a ```!discord``` command that will output the link ```https://discord.gg/butts```

change anything in output.py to make its generic responses a little more custom for oyu


you can hard code custom commands with somehting similar to below.
```py 
if message == '!example':
    send_message("example string)
```
```py
send_message("string")
``` 
will output string to twitch chat
```py
send_whisper(username, message) 
```
will whisper a target user

