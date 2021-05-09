import csv
from smtplib import SMTP, SMTP_SSL, SMTPConnectError


# Credit for creating (most of) this: https://github.com/acamso/demos/blob/master/_email/send_txt_msg.py
CARRIER_MAP = {
    'verizon': 'vtext.com',
    'tmobile': 'tmomail.net',
    't-mobile': 'tmomail.net',
    'sprint': 'messaging.sprintpcs.com',
    'at&t': 'txt.att.net',
    'boost': 'smsmyboostmobile.com',
    'cricket': 'sms.cricketwireless.net',
    'uscellular': 'email.uscc.net',
    'us cellular': 'email.uscc.net'
}

# A list of dicts of smtp servers, their email extensions, and their port number
SMTP_SERVERS = [{'Email extension': 'gmail.com', 'Port number': '587', 'SMTP server': 'smtp.gmail.com'},
 {'Email extension': 'outlook.com', 'Port number': '587', 'SMTP server': 'smtp.live.com'},
 {'Email extension': 'yahoo.com', 'Port number': '465', 'SMTP server': 'smtp.mail.yahoo.com'},
 {'Email extension': 'aol.com', 'Port number': '587', 'SMTP server': 'smtp.aol.com'},
 {'Email extension': 'hotmail.com', 'Port number': '465', 'SMTP server': 'smtp.live.com'},
 {'Email extension': 'comcast.net', 'Port number': '587', 'SMTP server': 'smtp.comcast.net'},
 {'Email extension': 'verizon.net', 'Port number': '465', 'SMTP server': 'outgoing.verizon.net'},
 {'Email extension': 'icloud.com', 'Port number': '587', 'SMTP server': 'smtp.mail.me.com'},
 {'Email extension': 'zohomail.com', 'Port number': '465', 'SMTP server': 'smtp.zoho.com'}]

class CarrierNotFound(Exception):
    pass
class CouldNotConnectToServer(Exception):
    pass
class InvalidRecipient(Exception):
    pass
class NoSMTPServer(Exception):
    pass
class NoPortNumber(Exception):
    pass


class Sender:
    '''An object that logs into an email account to send text messages.
    
    Attributes:
        email (str): The email address being used
        passwd (str): The password of the email address
        smtp_server (str): The SMTP server that will be connected to
        port (str): The port used to connect to the SMTP server
    
    Methods:
        __init__: Create a Sender with a given email & password (and optionally an smtp server and port)
    '''
    
    def __init__(self, email, passwd, smtp_server=None, port=None):
        '''Create a Sender to send text messages.
        
        Arguments:
            email (str): The email to be used. Ex: johnsmith@outlook.com
            passwd (str): The password of the email. Ex: password123
        
        Keyword arguments:
            smtp_server (str): The SMTP server of the email's domain. Ex: smtp.gmail.com
            port (int): The port number to be connected to. Ex: 587
        
        Raises:
            NoPortNumber: A port number was not provided nor found, so pass one as an argument.
            NoSMTPServer: An SMTP server was not provided nor found, so pass one as an argument.
        
        Returns:
            None
        '''
        
        # Set email and password
        self.email = email
        self.passwd = passwd

        if not smtp_server:
            # Try to get the email extension from the email
            try:
                email_ext = email.split('@')[1]
            except IndexError:
                raise NoSMTPServer('An SMTP server was not provided nor found')

            else:
                # Try to find the SMTP server from the email extension
                for server in SMTP_SERVERS:
                    if email_ext == server['Email extension']:
                        smtp_server = server['SMTP server']
                        self.smtp_server = smtp_server
                        
                        # Get the port if it isn't provided
                        if not port:
                            port = server['Port number']
                            self.port = port
                            return

                        break

                # An SMTP server wasn't found, so an exception is raised
                if not smtp_server:
                    raise NoSMTPServer('An SMTP server was not provided nor found')
        
        # An SMTP server was provided, so set it to that
        else:
            self.smtp_server = smtp_server
        
        if not port:
            # Try to find the port using the SMTP server
            for server in SMTP_SERVERS:
                
                if smtp_server == server['SMTP server']:
                    self.port = server['Port number']
                    return

            # A port wasn't found, so an exception is raised
            raise NoPortNumber('A port number was not provided nor found. Common port numbers include 587 and 465; maybe try one of those?')
        
        # A port number was provided, so set it to that
        else:
            self.port = port
    

    def text(self, recipient, message, carrier=None):
        '''
        Send a text message from the Sender's email.
        
        Arguments:
            recipient (str): The phone number to be texted. It's recommended that it includes the SMS gateway domain (e.g. "1234567890@vtext.com"). Otherwise, the format should be "1234567890".
            message (str): The message to be sent.
        
        Keyword arguments:
            carrier (str): The carrier of the recipient (e.g. Verizon). Only a few of the most popular carriers are supported; including the SMS gateway domain in recipient is recommended over using this.
        
        Raises:
            CarrierNotFound: A carrier was provided, but it couldn't be found. Please look up the SMS gateway domain of the carrier and include it in the recipient argument.
            CouldNotConnectToServer: The SMTP server could not maintain a connection.
            InvalidRecipient: The recipient doesn't have an @ symbol in it (and therefore does not contain the SMS gateway domain), and no carrier is provided.
        
        Returns:
            None
        '''
    
        # The phone number isn't complete, so the program tries to find what's missing
        if '@' not in recipient:
            
            # A carrier isn't provided, so nothing can be done. Raise an exception.
            if not carrier:
                raise InvalidRecipient('The recipient of the text message is invalid. It have an @ symbol in it and look like an email address.')
            
            carrier = carrier.lower()
            
            # If the carrier is found, change the recipient to be a valid SMS gateway
            if carrier in CARRIER_MAP:
                recipient += '@' + CARRIER_MAP[carrier]
            # Carrier wasn't found, raise an exception
            else:
                raise CarrierNotFound('A carrier wasn\'t found. Try changing the recipient to include the SMS gateway domain.')
        
        # If the port is 587, start with TLS
        if self.port == 587:
            server = SMTP(self.smtp_server, self.port)
            server.starttls()
        
        # If the port is 465, start with SSL
        elif self.port == 465:
            server = SMTP_SSL(self.smtp_server, self.port)
        
        # Try both TLS and SSL
        else:
            try:
                server = SMTP(self.smtp_server, self.port)
            except SMTPConnectError:
                server = SMTP_SSL(self.smtp_server, self.port)
            else:
                server.starttls()

        # Confirm that the server is connected
        if server.ehlo()[0] != 250:
            raise CouldNotConnectToServer('Failed to connect to the SMTP server.')
        
        # Log in to the email address
        server.login(self.email, self.passwd)
        
        # Send the mail
        server.sendmail(self.email, recipient, 'Subject:\n\n' + message) # TODO: This might be vulnerable to something similar to a SQLi attack. Prevent that from happening.
        server.quit()