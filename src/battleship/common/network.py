from .protocol import ProtocolMessage

class BattleShipWriterQueue:
    def __init__(self, writer):
        self.writer = writer
        self.pending_msgs = []

    def send(self, msg: ProtocolMessage):
        self.pending_msgs.append(msg)
