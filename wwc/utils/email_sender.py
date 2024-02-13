import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from wwc.utils.config import WwcConfig

cfg = WwcConfig()


class EmailSender:

    def __init__(self, result):
        self._result = result

    def send_email(self):
        html_content = '''
        <html>
        <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #ffffff; } /* Fond blanc pour tout le corps de l'email */
            .email-container { max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; }
            .title { font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 30px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; } /* Style pour le titre */
            .shop-title { font-size: 20px; font-weight: bold; color: #007bff; text-align: center; margin-top: 20px; margin-bottom: 10px; } /* Style pour mettre en valeur les noms des boutiques */
            .header { text-align: center; margin-bottom: 20px; }
            .header img { max-width: 100px; }
            .wine-container { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; margin-bottom: 20px; padding: 10px; }
            .wine-image { flex: 100%; max-width: 100%; margin-right: 20px; box-sizing: border-box; }
            .wine-image img { max-width: 100%; height: auto; border-radius: 8px; }
            .wine-info { flex: 1 0 auto; width: 100%; }
            .wine-name { font-size: 18px; font-weight: bold; color: #333; margin: 0; }
            .wine-price { font-size: 16px; color: #888; margin: 5px 0; }
            .wine-link { text-decoration: none; color: #007bff; font-size: 16px; }

            @media only screen and (min-width: 600px) {
                .wine-image { flex: 0 0 auto; width: 30%; }
                .wine-info { flex: 1 0 auto; }
            }
        </style>
        </head>
        <body>
        <div class="email-container">
            <div class="title">Wine Web Checker Report</div>
        '''

        for shop_dict in self._result:
            for shop, wines in shop_dict.items():
                html_content += f'<h2 style="text-align: center;">{shop.replace("_", " ").title()}</h2>'
                for wine in wines:
                    name = wine['name']
                    price = wine['price']
                    link = wine['link']
                    image_url = wine['image']['url']
                    html_content += f'''
                    <div class="wine-container">
                        <div class="wine-image">
                            <img src="{image_url}" alt="{name}">
                        </div>
                        <div class="wine-info">
                            <p class="wine-name">{name}</p>
                            <p class="wine-price">Price: {price}</p>
                            <a href="{link}" class="wine-link">View Product</a>
                        </div>
                    </div>
                    '''

        html_content += '''
            </div>
        </body>
        </html>
        '''

        gmail_user = "winewebsitechecker@gmail.com"
        gmail_app_password = cfg.password_gmail
        receiver_email = "udansin@hotmail.fr"
        subject = f"Wine Website Checker - Report {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = gmail_user
        msg['To'] = receiver_email
        msg['Reply-To'] = gmail_user

        part1 = MIMEText("No plain txt", 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_app_password)
            server.sendmail(gmail_user, receiver_email, msg.as_string())
            server.close()

            print('Email sent!')
        except Exception as exception:
            print("Error: %s!\n\n" % exception)
