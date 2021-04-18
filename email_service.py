import boto3
import json
import logging

class EmailService:
    def __init__(self,logger):
        self.__ses_client__ = boto3.client('ses')
        self.__logger__ = logger
        self.__logger__.setLevel(logging.INFO)
    def send_verification_email(self,email_address):
        return self.__ses_client__.verify_email_identity(EmailAddress = email_address)
    def verify_email_addresses(self, email_addresses):
        verification_attributes = self.__ses_client__.get_identity_verification_attributes(
            Identities = email_addresses
        )
        flag = True
        for email_address in verification_attributes['VerificationAttributes'].keys():
            status = verification_attributes['VerificationAttributes'][email_address]['VerificationStatus']
            if status != 'Success':
                flag = False
                self.__logger__.info("""Email address {} is not verified. Sending verification email to complete
                                     verification process. Please expect email from AWS Simple Email Service in few moments""".format(email_address))
                self.send_verification_email(email_address=email_address)
        return flag

    def send_alert_notification(self,email_addresses):
        if self.verify_email_addresses(email_addresses):
            self.__logger__.info("All emails addresses successfully verified. Sending alert notification...")
            recipients = json.load(open('recipients_template.json','r'))
            recipients['ToAddresses'] = email_addresses
            message = json.load(open('email_template.json','r'))
            sender = email_addresses[0]
            response = self.__ses_client__.send_email(
                Source = sender,
                Destination = recipients,
                Message = message,
            )
            self.__logger__.info(response)
        else:
            self.__logger__.critical("Email address verification failed. Aborting alert notification...")

