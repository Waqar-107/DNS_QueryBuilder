# from dust i have come, dust i will be

import socket

class dns_query:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.msg = ""
        self.query_type = 0
        self.query_no = 1
        self.recursiveQuery = True
        self.truncated = False
        self.questionQuantity = 1
        
        
    def getBinary(self, number, digit):
        s = ""
        while number > 0:
            s += chr(number % 2 + ord('0'))
            number //= 2
        
        while len(s) < digit:
            s += '0'
            
        s = s[:: -1]
        return s
        
        
    # 0 : a standard query (QUERY), 1 : an inverse query (IQUERY), 2 : a server status request (STATUS)
    def setQueryType(self, query_type):
        self.query_type = query_type
        
        
    # set true or false - true by default 
    def setRecusiveQuery(self, flag):
        self.recursiveQuery = flag
    
    
    # set the number of questions
    def setQuestionQuantity(self, q):
        self.questionQuantity = q
        
        
    def buildHeader(self):
        header = ""
        
        # same will be returned in the response of the query - 16 bits
        ID = self.getBinary(self.query_no, 16)
        self.query_no += 1
        
        # 1 4 1 1 1 1 3 4
        # |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
        QR = "0"
        
        opcode = self.getBinary(self.query_type, 4)
        
        AA = "0"
        TC = "1" if self.truncated else "0"
        RD = "1" if self.recursiveQuery else "0"
        RA = "0"
        
        Z = "000"
        RCODE = "0000"
        
        #number of questions
        QDCOUNT = self.getBinary(self.questionQuantity, 16)
        
        ANCOUNT = self.getBinary(0, 16)
        NSCOUNT = self.getBinary(0, 16)
        ARCOUNT = self.getBinary(0, 16)
        
        temp = ID + QR + opcode + AA + TC + RD + RA + Z + RCODE + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT
        
        # make the binary header hex
        for i in range(0, len(temp), 4):
            hx = hex(int(temp[i : i + 4], 2))
            header += hx[2 : ]
        
        return header
        
    
    def buildQuestion(self, domain_name) :
        question_section = ""
    
        partitions = domain_name.split('.')
        print(partitions)
    
        QNAME = ""
        for p in partitions : 
            QNAME += self.getBinary(len(p), 8)
            
            for i in range(len(p)):
                QNAME += self.getBinary(ord(p[i]), 8)
        
        # end of the domain
        QNAME += self.getBinary(0, 8)
        
        # The DNS record type we’re looking up. We’ll be looking up A records, whose value is 1.
        QTYPE = self.getBinary(1, 16)
        
        # The class we’re looking up. We’re using the the internet, IN, which has a value of 1
        QCLASS = self.getBinary(1, 16)
        
        temp_question = QNAME + QTYPE + QCLASS
        
        # convert the question into hex
        # do not use extra padding!!!
        for i in range(0, len(temp_question), 4):
            hx = hex(int(temp_question[i : i + 4], 2))
            question_section += hx[2 : 0]
        
        for i in range(0, len(question_section), 2):
            print(question_section[i : i + 2], end=" ")
            
        return question_section
    
    
    def getIP(self, domain_name):
        self.domain_name = domain_name
        
        self.buildQuestion(domain_name);
        
        return "127.0.0.1"

q = dns_query("8.8.8.8", 53)
q.getIP("example.com")