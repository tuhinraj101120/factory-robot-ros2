"""Conservative ultrasonic safety flag. It does not directly stop the base."""
import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from std_msgs.msg import Bool


class UltrasonicGuard(Node):
    def __init__(self):
        super().__init__("ultrasonic_guard")
        self.declare_parameter("stop_distance", 0.25)
        self.declare_parameter("range_topic", "/ultrasonic/range")
        self.declare_parameter("timeout_sec", 0.5)
        self.stop_distance = float(self.get_parameter("stop_distance").value)
        self.timeout = float(self.get_parameter("timeout_sec").value)
        topic = self.get_parameter("range_topic").value
        self.last_range = None
        self.last_rx = None
        self.sub = self.create_subscription(Range, topic, self.cb, 10)
        self.pub = self.create_publisher(Bool, "/safety/obstacle", 10)
        self.timer = self.create_timer(0.05, self.check)

    def cb(self, msg):
        self.last_range = msg
        self.last_rx = time.monotonic()

    def check(self):
        blocked = True
        if self.last_range is not None and self.last_rx is not None:
            r = self.last_range.range
            valid = (math.isfinite(r)
                     and self.last_range.min_range <= r <= self.last_range.max_range
                     and time.monotonic() - self.last_rx <= self.timeout)
            blocked = (not valid) or (r < self.stop_distance)
        out = Bool()
        out.data = blocked
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicGuard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
