#!/usr/bin/python

# Twisted Imports
from twisted.words.protocols.jabber import client, jid, xmlstream 
from twisted.names.srvconnect import SRVConnector
from twisted.words.xish import domish
from twisted.internet import reactor
from supervisor import childutils
import sys


doc = """\
crashxmpp.py [-p processname] [-a] [-m mail_addresses] [-u username] 
             [-w password] [-s jabberserver] [-r resource]

Options:

-p -- specify a supervisor process_name.  Send notification when this process
      transitions to the EXITED state unexpectedly. If this process is
      part of a group, it can be specified using the
      'process_name:group_name' syntax.
      
-a -- Send notification when any child of the supervisord transitions
      unexpectedly to the EXITED state unexpectedly.  Overrides any -p
      parameters passed in the same crashmail process invocation.


-m -- specify account names.  The script will send message to these
      accounts when crashxmpp detects a process crash.  

-u -- specify username for connect to jabber server. 

-w -- specify password for connect to jabber server. 

-r -- specify jabber resource name. default "crashxmpp"

-o -- specify jabber port number name. default "5222"

The -p option may be specified more than once, allowing for
specification of multiple processes.  Specifying -a overrides any
selection of -p.

A sample invocation:

crashxmpp.py -p program1 -p group1:program2 -m dev@example.com

"""



def usage():
    print doc
    sys.exit(255)


class CrashXMPP(object):

    def __init__(self, programs, any, emails, username, password, jabberserver, resource="crashxmpp", port=5222):
        self.programs = programs
        self.any = any
        self.emails = emails
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
        self.resource = resource
        self.username = username
        self.jabberserver = jabberserver
        self.password = password
        self.jabberport = port
        self.start()
        
    def alert(self, user):     
       message = domish.Element((None,'message'))
       message["to"] = user
       message["type"] = "chat"       
       message.addElement("body", content=self.message)       
       self.xmlstream.send(message)
       
    def stop(self):                        
        reactor.stop()
        
        
    def authd(self, xmlstream):   
       presence = domish.Element((None, 'presence'))
       presence.addElement('status').addContent('crashxmpp !!!')
       self.xmlstream = xmlstream
       self.xmlstream.send(presence)
       for email in self.emails:         
         self.alert(email)       
       
       
    def start(self):       
       myJid = jid.JID(self.username)
       factory = client.XMPPClientFactory(myJid, self.password)
       factory.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, self.authd)       
       connector = SRVConnector(reactor, 'xmpp-client', self.jabberserver, factory)       
       reactor.callLater(5, self.stop)
       connector.connect()    
 
    def run(self): 
       reactor.run()   
       
    def runforever(self):
        while True:        
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)
            if headers['eventname'] == 'PROCESS_STATE_EXITED':                
               pheaders, pdata = childutils.eventdata(payload+'\n')     
               if int(pheaders['expected']) == 0:        
                  self.message = ('Process %(processname)s in group %(groupname)s exited '
                         'unexpectedly (pid %(pid)s) from state %(from_state)s' %
                           pheaders)
                  self.run()                 
            childutils.listener.ok(self.stdout)

       
def main(argv=sys.argv):
    import getopt
    short_args="hp:p:a:m:u:w:s:r:o:"
    long_args=[
        "help",
        "program=",
        "any",
        "email="
        "username=",
        "password=",
        "jabberserver=",
        "resource=",
        "jabberport="
        ]
    arguments = argv[1:]
    try:
        opts, args = getopt.getopt(arguments, short_args, long_args)
    except:
        usage()

    programs = []
    any = False
    email = []
    status = '200'    
    jabberserver = ""
    resource = ""
    username = ""
    password = ""
    port = 5222
    
    for option, value in opts:
        if option in ('-h', '--help'):
            usage()

        if option in ('-p', '--program'):
            programs.append(value)

        if option in ('-a', '--any'):
            any = True

        if option in ('-s', '--jabberserver'):
            jabberserver = value

        if option in ('-m', '--email'):
            if value.find(',')>0:
                email.extend(value.split(','))
            else:
               email.append(value)

        if option in ('-u', '--username'):
            username = value

        if option in ('-w', '--password'):
            password = value                   
            
        if option in ('-r', '--resource'):
            resource = value    
            
        if option in ('-o', '--port'):
            port = port
    prog = CrashXMPP(programs, any, email, username, password, jabberserver, resource, port)
    prog.runforever()
if __name__ == '__main__':
    main()
    