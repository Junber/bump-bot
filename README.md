# bump-bot
An idiosyncratic discord bot to schedule things. And more!

To use this, you need to:
- Install requirements from requirements.txt
- Add a file config/token.txt that contains the discord bot token
- (Optionally) configure bookstack (see below)
- (Optionally but you should do it) change config/config.json to fit your needs
- Run bump-bot/bump_bot.py


## Bookstack

To use bookstack export, add file config/bookstack.json with the following format:

```JSON
{
	"url" : "",
	"token id" : "",
	"token secret" : ""
}
```