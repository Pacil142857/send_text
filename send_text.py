import os
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL, SMTPConnectError
from typing import Union


# A dictionary mapping each carrier to its MMS domain
MMS_CARRIER_MAP = {
    'verizon': 'vzwpix.com',
    'tmobile': 'tmomail.net',
    't-mobile': 'tmomail.net',
    'sprint': 'pm.sprint.com',
    'at&t': 'mms.att.net',
    'boost': 'myboostmobile.com',
    'cricket': 'mms.cricketwireless.net',
    'uscellular': 'mms.uscc.net',
    'us cellular': 'mms.uscc.net'
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


class SendTextError(Exception):
    '''Base class for all exceptions'''
class CarrierNotFound(SendTextError):
    pass
class CouldNotConnectToServer(SendTextError):
    pass
class InvalidRecipient(SendTextError):
    pass
class NoPortNumber(SendTextError):
    pass
class NoSMTPServer(SendTextError):
    pass
class SenderNotStarted(SendTextError):
    pass


class Sender:
    '''An object that logs into an email account to send text messages.
    
    Attributes:
        email (str): The email address being used
        passwd (str): The password of the email address
        port (int): The port used to connect to the SMTP server
        server (SMTP/SMTP_SSL): The object used to make & maintain a connection with the SMTP server
        smtp_server (str): The SMTP server that will be connected to
    
    Methods:
        __init__: Create a Sender with a given email & password (and optionally an smtp server and port)
        quit: Close the connection from the SMTP server
        start: Connect to the SMTP server and log in
        text: Send a text message to a given phone number
        text_image: Text an image to a given phone number
        text_video: Text a video to a given phone number
    '''    
    
    def __init__(self, email: str, passwd: str, smtp_server: str=None, port: str=None) -> None:
        '''Create a Sender object to send text messages.

        Args:
            email (str): The email to be used. Ex: johnsmith@gmail.com
            passwd (str): The password of the email. Ex: password123
            smtp_server (str, optional): The SMTP server of the email's domain. Ex: smtp.gmail.com.
            port (str, optional): The port number to be connected to. Ex: 587.

        Raises:
            NoPortNumber: A port number was not provided nor found, so pass one as an argument.
            NoSMTPServer: An SMTP server was not provided nor found, so pass one as an argument.
        
        Returns:
            None
        '''
        
        # Set email and password
        self.email: str = email
        self.passwd: str = passwd

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
                        self.smtp_server: str = smtp_server
                        
                        # Get the port if it isn't provided
                        if not port:
                            port = server['Port number']
                            self.port: int = port
                            return

                        break

                # An SMTP server wasn't found, so an exception is raised
                if not smtp_server:
                    raise NoSMTPServer('An SMTP server was not provided nor found')
        
        # An SMTP server was provided, so set it to that
        else:
            self.smtp_server: str = smtp_server
        
        if not port:
            # Try to find the port using the SMTP server
            for server in SMTP_SERVERS:
                
                if smtp_server == server['SMTP server']:
                    self.port: int = server['Port number']
                    return

            # A port wasn't found, so an exception is raised
            raise NoPortNumber('A port number was not provided nor found. Common port numbers include 587 and 465; maybe try one of those?')
        
        # A port number was provided, so set it to that
        else:
            self.port: int = port
    

    def start(self):
        '''Connects to the SMTP server and logs in.'''
        # If the port is 587, start with TLS
        if self.port == 587:
            self.server: SMTP = SMTP(self.smtp_server, self.port)
            self.server.starttls()
        
        # If the port is 465, start with SSL
        elif self.port == 465:
            self.server: SMTP_SSL = SMTP_SSL(self.smtp_server, self.port)
        
        # Try both TLS and SSL
        else:
            try:
                self.server: Union[SMTP, SMTP_SSL] = SMTP(self.smtp_server, self.port)
            except SMTPConnectError:
                self.server: Union[SMTP, SMTP_SSL] = SMTP_SSL(self.smtp_server, self.port)
            else:
                self.server.starttls()

        # Confirm that the server is connected
        if self.server.ehlo()[0] != 250:
            raise CouldNotConnectToServer('Failed to connect to the SMTP server.')
        
        # Log in to the email address
        self.server.login(self.email, self.passwd)
    
    
    def quit(self):
        '''Disconnects from the SMTP server.'''
        self.server.quit()


    def __enter__(self):
        '''Connect to the SMTP server and log in'''
        self.start()
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Disconnect from the SMTP server'''
        self.quit()


    def text(self, recipient: str, message: str, carrier: str=None) -> None:
        '''Send a text message from the Sender's email

        Args:
            recipient (str): The phone number to be texted.
                It's recommended that it includes the MMS gateway domain (e.g. "1234567890@vzwpix.com"). Otherwise, the format should be "1234567890".
            message (str): The message to be sent
            carrier (str, optional): The carrier of the recipient (e.g. Verizon). This is only required if you don't include the MMS gateway domain in recipient.
                Only a few of the most popular carriers are supported; including the MMS gateway domain in recipient is recommended over using this.

        Raises:
            CarrierNotFound: A carrier was provided, but it couldn't be found. Please look up the MMS gateway domain of the carrier and include it in the recipient argument.
            InvalidRecipient: The recipient doesn't have an @ symbol in it (and therefore does not contain the MMS gateway domain), and no carrier is provided.
            SenderNotStarted: The Sender object used has not been started. You probably forgot to call Sender.start and Sender.quit if you see this.
        '''        
    
        # The phone number isn't complete, so the program tries to find what's missing
        if '@' not in recipient:
            
            # A carrier isn't provided, so nothing can be done. Raise an exception.
            if not carrier:
                raise InvalidRecipient('The recipient of the text message is invalid. It have an @ symbol in it and look like an email address.')
            
            carrier = carrier.lower()
            
            # If the carrier is found, change the recipient to be a valid MMS gateway
            if carrier in MMS_CARRIER_MAP:
                recipient += '@' + MMS_CARRIER_MAP[carrier]
            # Carrier wasn't found, raise an exception
            else:
                raise CarrierNotFound('A carrier wasn\'t found. Try changing the recipient to include the MMS gateway domain.')
        
        # Create the message
        msg = MIMEText(message, 'plain', 'utf-8')
        
        # Send the mail
        try:
            self.server.sendmail(self.email, recipient, msg.as_string())
        except AttributeError:
            raise SenderNotStarted('The Sender object has not been started. Did you forget to call Sender.start (and Sender.quit)?')
    
    
    def text_image(self, recipient: str, image: str, carrier: str=None) -> None:
        '''Text the recipient an image from the Sender's email.

        Args:
            recipient (str): The phone number to be texted.
                It's recommended that it includes the MMS gateway domain (e.g. "1234567890@vzwpix.com"). Otherwise, the format should be "1234567890".
            image (str): The path of the image to be sent. Ex: "./path/to/image.png"
            carrier (str, optional): The carrier of the recipient (e.g. Verizon). This is only required if you don't include the MMS gateway domain in recipient.
                Only a few of the most popular carriers are supported; including the MMS gateway domain in recipient is recommended over using this.

        Raises:
            CarrierNotFound: A carrier was provided, but it couldn't be found. Please look up the MMS gateway domain of the carrier and include it in the recipient argument.
            InvalidRecipient: The recipient doesn't have an @ symbol in it (and therefore does not contain the MMS gateway domain), and no carrier is provided.
            SenderNotStarted: The Sender object used has not been started. You probably forgot to call Sender.start and Sender.quit if you see this.
        '''        
    
        # The phone number isn't complete, so the program tries to find what's missing
        if '@' not in recipient:
            
            # A carrier isn't provided, so nothing can be done. Raise an exception.
            if not carrier:
                raise InvalidRecipient('The recipient of the text message is invalid. It have an @ symbol in it and look like an email address.')
            
            carrier = carrier.lower()
            
            # If the carrier is found, change the recipient to be a valid MMS gateway
            if carrier in MMS_CARRIER_MAP:
                recipient += '@' + MMS_CARRIER_MAP[carrier]
            # Carrier wasn't found, raise an exception
            else:
                raise CarrierNotFound('A carrier wasn\'t found. Try changing the recipient to include the MMS gateway domain.')
        
        # Get the image data
        with open(image, 'rb') as f:
            img_data = f.read()
        
        # Create the image and have its filename be retained upon sending it
        img = MIMEImage(img_data, name=os.path.basename(image))
        img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image))
        
        # Attach the image to a blank message
        msg = MIMEMultipart()
        msg.attach(img)
        
        # Send the mail
        try:
            self.server.sendmail(self.email, recipient, msg.as_string())
        except AttributeError:
            raise SenderNotStarted('The Sender object has not been started. Did you forget to call Sender.start (and Sender.quit)?')


    def text_video(self, recipient: str, video: str, carrier: str=None) -> None:
        '''Text the recipient a video from the Sender's email.

        Args:
            recipient (str): The phone number to be texted.
                It's recommended that it includes the MMS gateway domain (e.g. "1234567890@vzwpix.com"). Otherwise, the format should be "1234567890".
            video (str): The path of the video to be sent. Ex: "./path/to/image.png"
            carrier (str, optional): The carrier of the recipient (e.g. Verizon). This is only required if you don't include the MMS gateway domain in recipient.
                Only a few of the most popular carriers are supported; including the MMS gateway domain in recipient is recommended over using this.

        Raises:
            CarrierNotFound: A carrier was provided, but it couldn't be found. Please look up the MMS gateway domain of the carrier and include it in the recipient argument.
            InvalidRecipient: The recipient doesn't have an @ symbol in it (and therefore does not contain the MMS gateway domain), and no carrier is provided.
            SenderNotStarted: The Sender object used has not been started. You probably forgot to call Sender.start and Sender.quit if you see this.
        '''        
    
        # The phone number isn't complete, so the program tries to find what's missing
        if '@' not in recipient:
            
            # A carrier isn't provided, so nothing can be done. Raise an exception.
            if not carrier:
                raise InvalidRecipient('The recipient of the text message is invalid. It have an @ symbol in it and look like an email address.')
            
            carrier = carrier.lower()
            
            # If the carrier is found, change the recipient to be a valid MMS gateway
            if carrier in MMS_CARRIER_MAP:
                recipient += '@' + MMS_CARRIER_MAP[carrier]
            # Carrier wasn't found, raise an exception
            else:
                raise CarrierNotFound('A carrier wasn\'t found. Try changing the recipient to include the MMS gateway domain.')
        
        # Get the video data
        with open(video, 'rb') as f:
            vid_data = f.read()
        
        # Create the video and encode it
        vid = MIMEBase('application', 'octet-stream')
        vid.set_payload(vid_data)
        encode_base64(vid)
        
        # Have the video retain its filename after being sent
        vid.add_header('Content-Disposition', 'attachment', filename=os.path.basename(video))
        
        # Attach the video to a blank message
        msg = MIMEMultipart()
        msg.attach(vid)
        
        # Send the mail
        try:
            self.server.sendmail(self.email, recipient, msg.as_string())
        except AttributeError:
            raise SenderNotStarted('The Sender object has not been started. Did you forget to call Sender.start (and Sender.quit)?')