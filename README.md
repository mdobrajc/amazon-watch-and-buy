# I want a 50 Series Nvidia card

## Disclaimer

USE AT YOUR OWN RISK!

This script was partially AI generated.
I published it only after being successful with my purchase, so in my case it worked, however there is no guarantee it'll work for you.

Feel free to make changes to the code or use it in any way you like, however I am not liable for any damages that may occur through the usage or modification of this project.

**Important advice**:

1. Don't mix 5090's with 5080's or you might buy a scalped product - for example 5080 for 2800€, even though your limit was meant for 5090.
2. The price is checked on the product and in the cart, therefor make sure your cart was and stays empty.
3. The order of Product IDs is your "priority list". Don't put a Suprim SOC at the end, if that's the one you want the most.

## Prerequisites

Install Python 3.11.9 from their [website](https://www.python.org/downloads/).
Install selenium `pip install selenium`
Install python-dotenv `pip install python-dotenv`
Install amazoncaptcha `pip install amazoncaptcha`
Download the corresponding WebDriver for your browser (Google -> ChromeDriver, GeckoDriver, MsEdgeDriver)
Put the driver into the script folder so it's easier to access.

## Setting Up Environment Variables

1. Copy the `.env.example` file to `.env`
2. Update the values

| Key          | Example                          | Meaning                                                                                                                                     |
| ------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| BROWSER      | chrome                           | chrome, firefox - which browser and driver you want to use                                                                                  |
| DRIVER_PATH  | chromedriver.exe                 | Path to the driver for your browser. In the example the driver is in the same folder as the script.                                         |
| AMZ_URL      | https://www.amazon.de/           | Amazon URL                                                                                                                                  |
| AMZ_EMAIL    | AzureDiamond@fake-email.com      | Your Amazon E-mail.                                                                                                                         |
| AMZ_PWD      | hunter2                          | Your Amazon Password.                                                                                                                       |
| MFA          | 0                                | 0 if you don't use MFA, 1 if you do.                                                                                                        |
| BMFA_TIMEOUT | 120                              | Bank MFA timeout. With 120 you have 2 minutes time to approve on your banking app, otherwise the script will clear the cart and start over. |
| PRODUCTS     | B0DT6SN14V;B0DT6Q3BXM;B0DT6S77JK | Semicolon separated IDs. The example is for the MSI 5090 Suprim SOC, Gaming Trio, Ventus.                                                   |
| MAX_PRICE    | 3000                             | Set your limit how much you want to spend.                                                                                                  |

## How does it work?

It's split in two parts.

Part 1 (headless - no browser window)

- checking if there is anything in stock and under the price limit
- triggering the purchase in part 2 as soon as one in stock is detected

Part 2 (with browser window)

- prepares the login to amazon (beforehand)
- waits for the trigger
- executes the purchase

Important to note is, that the script doesn't handle all special cases that might occur on the checkout screen.
It might cancel even if the purchase almost went through.

## Getting that unicorn

If you did everything, run the `run.bat` or use a terminal with `python script.py`

The script should hopefully stop on the first successful purchase, I do however recommend setting a limit on your card or use a space where you only have enough money for one purchase.

## Known Issues

- Login sometimes fails, because a completely different Amazon Homepage loads
- Captcha loads up

## Support

You don't need to, but if you're crazy enough and managed to finally get a 50 series card, feel free to drop a few cents to my ko-fi page.

https://ko-fi.com/mdobrajc
