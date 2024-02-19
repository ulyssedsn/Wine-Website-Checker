from requests import Session
from wwc.logic.factory import Factory
from wwc.utils.config import WwcConfig
from wwc.utils.email_sender import EmailSender

cfg = WwcConfig()
requests_session = Session()


def find_wine():
    all_websites_result = []
    for website in cfg.websites:
        print(f"--------- Checking {website} ---------")
        try:
            website_result = Factory.instance(
                'web', website, requests_session).search()
            if website_result:
                all_websites_result.append({website: website_result})
        except Exception as e:
            EmailSender().send_error_email(website, e)
    print(all_websites_result)
    if all_websites_result:
        EmailSender().send_email(all_websites_result)


find_wine()
