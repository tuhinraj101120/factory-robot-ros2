"""Camera topic smoke-test node; station detection is intentionally not implemented yet."""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class CameraPerception(Node):
    def __init__(self):
        super().__init__("camera_perception")
        self.declare_parameter("image_topic", "/camera/image_raw")
        topic = self.get_parameter("image_topic").value
        self.bridge = CvBridge()
        self.count = 0
        self.sub = self.create_subscription(Image, topic, self.cb, 10)
        self.get_logger().info(f"Listening for camera images on {topic}")

    def cb(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            self.count += 1
            if self.count % 30 == 0:
                self.get_logger().info(f"Received {self.count} images; frame={frame.shape[1]}x{frame.shape[0]}")
            # TODO: detect ArUco station tags after confirming camera calibration.
        except Exception as exc:
            self.get_logger().error(f"Image conversion failed: {exc}")


def main(args=None):
    rclpy.init(args=args)
    node = CameraPerception()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
