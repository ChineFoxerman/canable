#!/usr/bin/env python

import rospy
from can_msgs.msg import Frame
import can
from geometry_msgs.msg import Twist
import struct

PUB_TOPIC = 'tender_bot/cmd_vel'
NODE_NAME = 'tender_bot'
CAN_DEVICE_NAME = 'can0'
BUSTYPE = 'socketcan'
I = 0


class can_bus(can.Listener):
    def __init__(self, bus):
        self.canpub = rospy.Publisher(PUB_TOPIC, Twist, queue_size=10)
        self.bus = bus
        self.notifier = can.Notifier(bus, [self])

    def on_message_received(self, msg):
        cmd = Twist()
        can_frame = Frame()
        can_frame.data = msg.data
        can_frame.dlc = msg.dlc
        can_frame.id = msg.arbitration_id
        print(can_frame.data)
        if can_frame.id == 0x5FF:
            (mode, linear, angular, jockeyspeed)= struct.unpack('<Bhhh', can_frame.data)
            cmd.linear.x = float(linear)/1000
            cmd.angular.z = float(angular)/1000
            cmd.linear.z = float(jockeyspeed)
            print("mode %d \n"
                  "linear %d \n"
                  "angular %d \n"
                  "jockey %d \n" % (mode, linear, angular, jockeyspeed))
        else:
            print(False)
        self.canpub.publish(cmd)

    def send_message(self):
        global I
        msgs = can.Message(arbitration_id=0x7EE, data=[I, 0, 1, 2, 3, 4, 5, 0], is_extended_id=False)
        self.bus.send(msgs)
        I = I + 1
        if I == 200:
            I = 0


if __name__ == '__main__':
    rospy.init_node(NODE_NAME)
    bus = can.interface.Bus(CAN_DEVICE_NAME, bustype=BUSTYPE)
    r = rospy.Rate(10)
    try:
        while not rospy.is_shutdown():
            can_ros = can_bus(bus)
            # can_ros.send_message()
            r.sleep()
    except KeyboardInterrupt:
        bus.shutdown()
