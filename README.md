# 🤖 B.O.B. the break out bot
Simple Webex Teams bot to automate creating breakout spaces in a particular team.

## Commands
- **help**: Shows this help text.
- **breakout n**: Create breakout spaces and add _n_ number of team members to it.
- **cleanup**: Archive any breakout spaces that were created by the bot.

## Tools used
- The wonderful [webexteamssdk](https://github.com/CiscoDevNet/webexteamssdk)
- The fabulous [Flask](https://github.com/pallets/flask)
- The zany [Zappa](https://github.com/Miserlou/Zappa) for deploying to AWS lambda with _zero_ effort

_Built very rapidly, so no docs or testing._