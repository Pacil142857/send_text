import csv
from smtplib import SMTP


# This is how the program should work when finished
# my_email = Sender(username, password, smtp_server)
# my_email.send(number, message)

class NoSMTPServer(Exception):
    pass


class Sender:
    
    def __init__(self, email, passwd, smtp_server=None, port=None):
        # TODO: Provide a description on what this does
        
        # Set email and password
        self.email = email
        self.passwd = passwd
        

        if not smtp_server:
            
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
            
            try:
                email_ext = email.split('@')[1]
            except IndexError:
                raise NoSMTPServer('An SMTP server was not provided nor found')
            else:
                # Try to find the SMTP server
                for server in smtp_servers:
                    if email_ext == server['Email Extension']:
                        
                        smtp_server = server['SMTP Server']
                        
                        # Get the port if it isn't provided
                        if not port:
                            port = server['Port number']

                        return

                # An SMTP server wasn't found, so an exception is raised
                raise NoSMTPServer('An SMTP server was not provided nor found')
        
        # TODO: Get the port number