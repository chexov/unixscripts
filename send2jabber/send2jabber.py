#!/usr/bin/env python
# Anton P. Linevich <anton@linevich.com>. March, 2010
#
import sys
import os
import string
import getopt
import jabber

# Usage help
def usage():
    print ("Usage: send2jabber.py --user=Username --password=Password --server=jabber.myhostname.com --recipient=bill@gates.com")

def connect(Username, Server, Resource, Password):
    JID = Username + '@' + Server + '/' + Resource
    
    con = jabber.Client(host=Server)
    #jabber.xmlstream.ENCODING='koi8-r'
    
    try:
        con.connect()
        if not con.auth(Username,Password,Resource):
            raise ValueError("%s: %s" % (con.lastErrCode, con.lastErr) )
        return con
    except IOError, e:
        raise ValueError("Couldn't connect: %s" % e)

def send_msg(con, Recipient, txt=None, encoding='utf-8'):
    if not txt:
        txt = string.join (sys.stdin.readlines(),'')
    
    msg = jabber.Message(Recipient, txt.decode(encoding))
    msg.setTo(Recipient)
    msg.setType('chat')
    con.send(msg)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hspur:", ["server=", "password=", "user=", "recipient="])
    except getopt.GetoptError:
       # print help information and exit:
       usage()
       sys.exit(1)
    
    Recipient = None
    Username = None
    Server = None
    Password = None
    
    for o, a in opts:
        if o in ('-r', '--recipient'):
            Recipient = a
        elif o in ('-u', '--user'):
            Username = a
        elif o in ('-s', '--server'):
            Server = a
        elif o in ('-p', '--password'):
            Password = a
    
    Resource = "send2jabber"
    
    if not Recipient:
        print "Recipient is", Recipient
        usage()
        sys.exit(1)
    
    if not Username:
        print "Username is", Username
        usage()
        sys.exit(1)
    
    if not Server:
        print "Server is", Server
        usage()
        sys.exit(1)
    
    if not Password:
        print "Password is", Password
        usage()
        sys.exit(1)
    
    con = connect(Username, Server, Resource, Password)
    send_msg(con, Recipient)

if __name__ == "__main__":
    main()

