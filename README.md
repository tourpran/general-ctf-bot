## Instructions and Prerequisites to use this bot:
* Have a server to run the python script 24/7. (Platforms like heroku cant handle the bot since most free apps, go to sleep every fixed time period.)
* Have python3 and discord application installed on your system.
* OS: All Operting systems are supported.

## Creating the bot: 
* Go to [Discord Developers](https://discord.com/developers/applications) and create a new application. 
![1](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/ss1.jpg)
* Now that you have created the application, create the bot.
![2](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/ss2.jpg)

## Cloning this repository in your server:
```bash
> git clone https://github.com/pranavkrish04/general-ctf-bot.git
> rm -rf images
```
After cloning to the repository dont forget to go into the directory.

## Run the Bot:
In order to run the bot you need to go to your bot's BOT section and copy your secret TOKEN.
![3](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/ss3.jpg)
Now that you have the code copied just save that into your ``token.txt`` file.

### Installing requirements and starting the bot: 
```bash
> pip3 install -r requirements.txt
> python3 bot.py
```
## Inviting the bot to the server:
* Go to your OAuth2 section and click the bot option, then open the url generated to invite the bot to your server. 
![4](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/ss4.jpg)
It is always recomended to give admin permissions to the bot for having a smooth workflow and to have less/no errors.
* Go to your Bot section and click the server members intent switch
![5](//github.com/pranavkrish04/general-ctf-bot/blob/main/images/ss5.jpg)

## Usage: 
* Create a channel called ``_bot_query`` in your server. Use this channel solely for using bot commands. (Bot wont work in other channels)
* Try not to use spaces while creating a ctf category or a challenge channel. (bot under development).
* Whenever you are in doubt ``-help`` will show all commands.

## Some cool pics: 
### in _bot_query
![](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/s1.png)
### in joinctf
![](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/s2.png)
### in main channel of the ctf created
![](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/s3.png)
### in challenge channel
![](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/s4.png)
### in main everyone gets notified
![](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/s5.png)
### in main see all the challenges completed by others
![](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/s6.png)
### in main end the ctf and delete the roles and make the channels public
![](https://github.com/pranavkrish04/general-ctf-bot/blob/main/images/s7.png)

## Credits: 
[x0r19x91](https://github.com/x0r19x91) and [myself](https://github.com/pranavkrish04)

[nullpxl](https://github.com/NullPxl) for ctftime commands.
