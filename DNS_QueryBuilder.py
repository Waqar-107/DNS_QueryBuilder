# from dust i have come, dust i will be

import socket
import binascii


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

    # the binary representation will be returned, if the length is < desired digits then extra 0 is padded
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

        # number of questions
        QDCOUNT = self.getBinary(self.questionQuantity, 16)

        ANCOUNT = self.getBinary(0, 16)
        NSCOUNT = self.getBinary(0, 16)
        ARCOUNT = self.getBinary(0, 16)

        temp = ID + QR + opcode + AA + TC + RD + RA + Z + \
            RCODE + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

        # make the binary header hex
        for i in range(0, len(temp), 4):
            hx = hex(int(temp[i: i + 4], 2))
            header += hx[2:]

        return header

    def buildQuestion(self, domain_name):
        question_section = ""
        partitions = domain_name.split('.')

        QNAME = ""
        for p in partitions:
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
            hx = hex(int(temp_question[i: i + 4], 2))
            question_section += hx[2:]

        # for i in range(0, len(question_section), 2):
        #     print(question_section[i : i + 2], end=" ")

        self.question_len = len(question_section)

        return question_section

    def send_udp(self, msg):
        # no blank or newline
        msg = msg.replace(" ", "").replace("\n", "")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.sendto(binascii.unhexlify(msg), (self.server_ip, self.port))
            print("udp sent")

            data, address = sock.recvfrom(4096)
        finally:
            sock.close()

        return binascii.hexlify(data).decode("utf-8")

    def parseResponse(self, res, showReport):

        # ----------------------------------------
        # header
        head = []
        for i in range(0, 24, 4):
            head.append(res[i: i + 4])

        ID = head[0]
        flags = head[1]
        question_quantity = head[2]
        answer_quantity = head[3]
        authority_records = head[4]
        additional_records = head[5]

        # check id
        if(int(ID, 16) != self.query_no):
            print("error : id not matched")
            print("query-id :", self.query_no)
            print("response-id :", int(ID, 16))
            return "-1"

        self.query_no += 1

        # check flags
        flags = self.getBinary(int(flags, 16), 16)

        # 1 4 1 1 1 1 3 4
        # |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
        QR = flags[0]
        opcode = flags[1: 5]
        AA = flags[5]
        TC = flags[6]
        RD = flags[7]
        RA = flags[8]
        Z = flags[9: 12]
        RCODE = flags[12: 16]

        if int(RCODE, 2) != 0:
            print(RCODE, "error reported")
            return "-1"

        # additional info
        if showReport:
            print("No errors reported")

            if int(AA, 2) == 0:
                print("This server isn’t an authority for the given domain name")

            if int(RD, 2) == 1:
                print("Recursion was desired for this request")

            if int(RA, 2) == 1:
                print("Recursion is available on this DNS server")

        # ----------------------------------------

        # question section is the same as the query
        question = res[24: 24 + self.question_len]

        # ----------------------------------------
        # answer
        answer_section = res[24 + self.question_len:]

        # [12 : 16] => don't know the fuck it denotes, it is 00 00
        NAME = answer_section[0: 4]
        TYPE = answer_section[4: 8]
        CLASS = answer_section[8: 12]
        TTL = answer_section[16: 20]
        RDLENGTH = int(answer_section[20: 24], 16)
        RDDATA = answer_section[24:]

        if showReport:
            print("TTL :", int(TTL, 16), "seconds")
            print("RDLENGTH :", RDLENGTH, "bytes")

        ip_adress_chunks = []
        for i in range(0, RDLENGTH * 2, 2):
            ip_adress_chunks.append(str(int(RDDATA[i: i + 2], 16)))

        return ".".join(ip_adress_chunks)
        # ----------------------------------------

    def getIP(self, domain_name, showReport):
        header = self.buildHeader()
        question = self.buildQuestion(domain_name)

        res = self.send_udp(header + question)

        return self.parseResponse(res, showReport)
