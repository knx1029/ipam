
## return whether ip1 contains ip2
def ip_contain(ip1, ip2):
    while (ip2 > ip1):
        ip2 = (ip2 - 1) / 2
    return (ip1 == ip2)


class Entry:

    @classmethod
    def parse(cls, str):
        e = Entry()
        e.permit = ("->" in str)
        str = str.replace(" -> ", ";")
        str = str.replace(" \> ", ";")
        tokens = str.split(';')
        src = tokens[0]
        dst = tokens[-1]
        tokens = src.split(':')
        e.sip = int(tokens[0])
        e.sport = tokens[1]
        tokens = dst.split(':')
        e.dip = int(tokens[0])
        e.dport = tokens[1]
        return e

    def __init__(self):
        self.marked = False
        

    def set_fields(self, tokens, is_acl = True, standard = False):
        if (is_acl):
            int_tokens = map(lambda(x): int(x), tokens)
            self.sip = int_tokens[0]
            self.dip = int_tokens[1]
            self.sport = (int_tokens[2], int_tokens[3])
            self.dport = (int_tokens[4], int_tokens[5])
            self.proto = 0
            self.permit = int_tokens[6]
        elif (standard):
            id = 0
            self.permit = (tokens[id] == "permit")
            id = id + 1
            if (id + 1 < len(tokens) and ("." in tokens[id + 1])):
                self.sip = strip2intip(tokens[id], tokens[id + 1])
            elif (tokens[id] == "any"):
                self.sip = 0
            else:
                self.sip = strip2intip("host", tokens[id])
            self.dip = 0
            self.proto = 0
            self.sport = self.dport = None
        else:
            id = 0
            self.permit = (tokens[id] == "permit")
            id = id + 1
            self.proto = tokens[id]
            id = id + 1
            ## parse sip
            if (tokens[id] == "any"):
                self.sip = 0
                id = id + 1
            else:
                self.sip = strip2intip(tokens[id], tokens[id + 1])
                id = id + 2

            ## sparse sport
            self.sport = None
            if (id + 1 < len(tokens)):
                if (tokens[id] == 'eq'):
                    self.sport = tokens[id + 1]
                    id = id + 2
                elif (tokens[id] == 'range'):
                    self.sport = (tokens[id + 1], tokens[id + 2])
                    id = id + 3

            ## parse dip
            if (tokens[id] == "any"):
                self.dip = 0
                id = id + 1
            else:
                self.dip = strip2intip(tokens[id], tokens[id + 1])
                id = id + 2

            self.dport = None
            if (id + 1 < len(tokens)):
                if (tokens[id] == 'eq'):
                    self.dport = tokens[id + 1]
                    id = id + 2
                elif (tokens[id] == 'range'):
                    self.dport = (tokens[id + 1], tokens[id + 2])
                    id = id + 3
                

    def eq(self, e):
        return (self.sip == e.sip and
                self.dip == e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
                self.permit == e.permit)

    def src_shadow(self, e):
        return (self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
                self.dst_matched(e.dip))

    def dst_shadow(self, e):
        return (self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
                self.src_matched(e.sip))


    def src_matched(self, sip):
        return ip_contain(self.sip, sip)

    def dst_matched(self, dip):
        return ip_contain(self.dip, dip)

    def src_group(self, e):
        return (#self.sip != e.sip and
                self.dip == e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
                self.permit == e.permit)

    def dst_group(self, e):
        return (self.sip == e.sip and
                #self.dip != e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
                self.permit == e.permit)
        
    def __str__(self):
        if self.permit:
            ps = "->"
        else:
            ps = "\>"
        return "%d:%s %s %d:%s" % (self.sip, 
#        return "%s:%s %s %s:%s" % (intip2ip(self.sip),
                                   str(self.sport),
                                   ps,
                                   self.dip,
#                                   intip2ip(self.dip),
                                   str(self.dport))

    def readable_str(self):
        if self.permit:
            ps = "->"
        else:
            ps = "\>"
        return "%s:%s %s %s:%s" % (intip2ip(self.sip),
                                   str(self.sport),
                                   ps,
                                   intip2ip(self.dip),
                                   str(self.dport))


def strip2intip(s1, s2):
    def f(s):
        ls = s.rsplit('.')
        x = 0
        for l in ls:
            x = x << 8
            x = x + int(l)
        return x
    try:
        y = 0
        if (s1 == "host"):
            y = f(s2) + (1 << 32) - 1
        else:
            base = (1<<32) / (f(s2) + 1) - 1
            y = f(s1) / (f(s2) + 1) + base
    except ValueError, e:
        print "ERROR", s1, s2
        raise e
    return y

def intip2str(ip):
    s = ""
    while (ip > 0):
        if (ip % 2 == 0):
            s = "1" + s
        else:
            s = "0" + s
        ip = (ip - 1) / 2
    s = s + "*" * (32 - len(s))
    return s

def intip2ip(ip):
    l = 0
    n = 0
    while (ip > 0):
        if (ip % 2 == 0):
            n = n + (1<<l)
        l = l + 1
        ip = (ip - 1) / 2
    n = (n << (32 - l))
    ip = "{0}.{1}.{2}.{3}/{4}".format(n >> 24,
                                      (n >> 16) & 255,
                                      (n >> 8) & 255,
                                      n & 255,
                                      l)
    return ip
