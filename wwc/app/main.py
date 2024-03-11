from requests import Session
from wwc.logic.factory import Factory
from wwc.utils.config import WwcConfig
from wwc.utils.email_sender import EmailSender

cfg = WwcConfig()
requests_session = Session()


def find_wine():
    for user in cfg.users:
        all_websites_result = []
        print(f"Checking user: {user['email']}")
        for website in cfg.websites:
            print(f"--------- Checking {website} ---------")
            try:
                website_result = Factory.instance(
                    'web', website, user, requests_session).search()
                if website_result:
                    all_websites_result.append({website: website_result})
            except Exception as e:
                EmailSender(user).send_error_email(website, e)
        print(all_websites_result)
        if all_websites_result:
            EmailSender(user).send_email(all_websites_result)


find_wine()
