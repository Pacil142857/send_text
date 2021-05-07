import csv
from smtplib import SMTP


# This is how the program should work when finished
# my_email = Sender(username, password, smtp_server)
# my_email.send(number, message)

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
            NoSMTPServer: An SMTP server was not provided nor found, so pass one as an argument.
            NoPortNumber: A port number was not provided nor found, so pass one as an argument.
        
        Returns:
            None
        '''
        
        # Set email and password
        self.email = email
        self.passwd = passwd
        
        # Get the data from the "database" file
        if not smtp_server or not port:
            # Get list of smtp servers and their ports
            smtp_servers = []
            
            # Open the "database" of smtp servers
            with open('smtp_servers.csv') as f:
                reader = csv.reader(f)
                
                fields = next(reader)
                cur_row = dict()
                
                # Read the file and get the data
                # The data will be a list of dictionaries
                for row in reader:
                    for i, cell in enumerate(row):
                        cur_row[fields[i]] = cell
                    smtp_servers.append(cur_row.copy())

        if not smtp_server:
            # Try to get the email extension from the email
            try:
                email_ext = email.split('@')[1]
            except IndexError:
                raise NoSMTPServer('An SMTP server was not provided nor found')

            else:
                # Try to find the SMTP server from the email extension
                for server in smtp_servers:
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
            for server in smtp_servers:
                
                if smtp_server == server['SMTP server']:
                    self.port = server['Port number']
                    return

            # A port wasn't found, so an exception is raised
            raise NoPortNumber('A port number was not provided nor found. Common port numbers include 587 and 465; maybe try one of those?')
        
        # A port number was provided, so set it to that
        else:
            self.port = port