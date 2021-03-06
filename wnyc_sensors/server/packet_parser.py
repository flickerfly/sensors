PACKET_PARSE_CLASSES = {}

class ParseHitMiss():
    def pop_hit_miss(self):
        return self.pop_int(), self.pop_int()

class ParseFloat():
    def pop_float(self):
        return float(self.tokens.pop())

class Packet(str):
    def __init__(self, value):
        str.__init__(self, value)
        self.tokens = list(reversed(self.split(" ")))
        packet_type = self.pop()
        if packet_type not in PACKET_PARSE_CLASSES:
            raise ValueError("Invalid UDP packet.  Don't recognize packet type: " + repr(packet_type))
        self.__class__ = PACKET_PARSE_CLASSES[packet_type]
        self.hash = self.pop_hex()
        self.device = self.pop_int()
        self.version = self.pop_int()
        self.parse()

    def as_dict(self):
        return {'hash': self.hash,
                'device': self.device,
                'version': self.version,
                'packet_type': self.__class__.__name__}

    def pop_hex(self):
        return self.pop_int(16)

    def pop_int(self, base=10):
        return int(self.pop(), base)

    def pop(self):
        return self.tokens.pop()

    def pops(self, count=1):
        for _ in range(count):
            yield self.pop()
        

class CicadiaPacket(Packet, ParseHitMiss, ParseFloat):
    def as_dict(self):
        d = Packet.as_dict(self)
        d.update({'temp': self.temp,
                  'hit': self.hit,
                  'miss': self.miss})
        return d
                
    def parse(self):
        self.temp = self.pop_float()
        self.hit, self.miss = self.pop_hit_miss()
        

class FlasherPacket(Packet, ParseHitMiss):
    def as_dict(self):
        d = Packet.as_dict(self)
        d.update({'hit': self.hit,
                  'miss': self.miss})
        return d
    def parse(self):
        self.hit, self.miss = self.pop_hit_miss()

PACKET_PARSE_CLASSES['cicadia'] = CicadiaPacket
PACKET_PARSE_CLASSES['flashers'] = FlasherPacket
