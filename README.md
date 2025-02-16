# Gimme gimme gimme a 50' Series after midnight

## Disclaimer

**USE AT YOUR OWN RISK!**

The initial script was partially AI generated, but I refactored it to the current state.
My knowledge of python was built over the past 2 weeks fine tuning and refactoring the script.
My plan was to publish it after I was successful, but I went for a RTX 5080 instead, waiting until the RTX 5090 stock stabilises.

Feel free to make changes to the code or use it in any way you like, however I am not liable for any damages that may occur through the usage or modification of this project.

## Important advice

1. Don't mix 5090's with 5080's or you might buy a scalped product - for example 5080 for 2800€, even though your limit was meant for 5090.
2. The order of Product IDs is your "priority list". Don't put a Suprim SOC at the end, if that's the one you want the most.
3. Don't put too many products - you might miss the product to others
4. Don't put the delay too low - Amazon may throw errors
5. Disable MFA, Passkey, etc. Those cases weren't really tested.
6. This bot wasn't proven to work - as written, I settled with a 5080, so I can't guarantee success

## Prerequisites

Install Python 3.11.9 from their [website](https://www.python.org/downloads/).
Install selenium `pip install selenium`
Install python-dotenv `pip install python-dotenv`
Install amazoncaptcha `pip install amazoncaptcha`
Download the corresponding WebDriver for your browser (Google -> ChromeDriver, Firefox -> GeckoDriver, Edge -> MsEdgeDriver)
Put the driver into the script folder so it's easier to access.
Make sure you have the "Buy now" button enabled on your account.

## Setting Up Environment Variables

1. Copy the `.env.example` file to `.env`
2. Update the values

| Key          | Example                          | Meaning                                                                                             |
| ------------ | -------------------------------- | --------------------------------------------------------------------------------------------------- |
| BROWSER      | chrome                           | chrome, firefox - which browser and driver you want to use                                          |
| DRIVER_PATH  | chromedriver.exe                 | Path to the driver for your browser. In the example the driver is in the same folder as the script. |
| AMZ_URL      | https://www.amazon.de/           | Amazon URL                                                                                          |
| AMZ_EMAIL    | AzureDiamond@fake-email.com      | Your Amazon login E-mail.                                                                           |
| AMZ_PWD      | hunter2                          | Your Amazon login Password.                                                                         |
| AMZ_MFA      | 0                                | 0 if you don't use MFA, 1 if you do. If it's 0 the browser will run headless.                       |
| AMZ_PRODUCTS | B0DT6SN14V;B0DT6Q3BXM;B0DT6S77JK | Semicolon separated IDs. The example is for the MSI 5090 Suprim SOC, Gaming Trio, Ventus.           |
| AMZ_CURRENCY | €                                | The currency: €, $ - important because otherwise the price can't be found.                          |
| MAX_PRICE    | 3000                             | Set your limit how much you want to spend.                                                          |
| BMFA_TIMEOUT | 120                              | Bank MFA timeout. With 120 you have 2 minutes time to approve on your banking app.                  |
| LOOP_TIMEOUT | 5                                | How many seconds the loop waits, before starting the next check / purchase cycle                    |
| RETRY_COUNT  | 3                                | How many times the bot attempts to buy a product                                                    |

## How does it work?

The main function creates a new thread and starts the Amazon bot.
One could go and add additional modules for other websites, but I only made one for Amazon atm.

### Amazon Bot

2 drivers are created

Driver 1 (always headless - no browser window)

- doesn't login
- checking if there is anything in stock and under the price limit
- triggering the purchase in part 2 as soon as one in stock is detected

Driver 2 (depending on MFA, either headless or with a visible window)

- logs into amazon
- waits for an available product (found through driver 1)
- executes the purchase

Captchas are automatically solved, thanks to `amazoncaptcha`, which is also the reason I used Python 3.11.9.
The purchase is made with the "Buy now" button, so clearing the card isn't a prerequisite anymore.
Two types of the "Buy now" workflow are supported:

- buy now with turbo window (purchase not really tested)
- buy now with redirect to checkout (purchase tested once by accident)

## Getting that unicorn

If you did everything, use a terminal with `python main.py`.

The script should hopefully stop on the first successful purchase, I do however recommend setting a limit on your card or use a space where you only have enough money for one purchase.

## Known issues

- Login sometimes fails, because a completely different Amazon Homepage loads

## Support

I might not upkeep the project, but I wanted to share the code.

You don't need to, but if you're crazy enough and managed to snipe an Amazon product, feel free to drop a few cents to my ko-fi page.

https://ko-fi.com/mdobrajc
