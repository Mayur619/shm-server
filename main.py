from email_service import EmailService
import logging

if __name__ == '__main__' :
    service = EmailService(logger=logging.getLogger())
    email_addresses = ('mgiri6612@gmail.com','mgiri@horizon.csueastbay.edu')
    #for email in email_addresses:
    #    service.send_verification_email(email)
    service.send_alert_notification(email_addresses)
