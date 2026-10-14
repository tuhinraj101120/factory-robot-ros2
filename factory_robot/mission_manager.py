"""Simple Nav2 action-based delivery sequencer starter."""
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

# World-frame docking poses; replace with positions from your actual map.
STATIONS = {
    "S1": (-3.0, 2.5, math.pi),
    "S2": (3.0, 2.5, 0.0),
    "S3": (3.0, -2.5, 0.0),
    "S4": (-3.0, -2.5, math.pi),
}
HOME = (0.0, 0.0, 0.0)


def yaw_quaternion(yaw):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


class MissionManager(Node):
    def __init__(self):
        super().__init__("mission_manager")
        self.declare_parameter("orders", ["S1>S3", "S2>S4", "S3>S1"])
        self.declare_parameter("frame_id", "map")
        self.frame_id = self.get_parameter("frame_id").value
        raw_orders = self.get_parameter("orders").value
        self.orders = []
        for order in raw_orders:
            parts = str(order).upper().split(">")
            if len(parts) != 2 or parts[0] not in STATIONS or parts[1] not in STATIONS or parts[0] == parts[1]:
                raise ValueError(f"Invalid order {order!r}; expected e.g. S1>S3")
            self.orders.append((parts[0], parts[1]))
        self.client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.busy = False
        self.phase = "WAIT_NAV2"
        self.order_index = 0
        self.leg = "source"
        self.timer = self.create_timer(0.5, self.tick)
        self.get_logger().info(f"Mission ready with {len(self.orders)} orders")

    def tick(self):
        if self.busy:
            return
        if not self.client.server_is_ready():
            self.get_logger().info("Waiting for Nav2 action server: navigate_to_pose", throttle_duration_sec=5.0)
            return
        if self.order_index >= len(self.orders):
            if self.phase == "HOME_DONE":
                self.get_logger().info("Mission route complete.")
                self.timer.cancel()
            elif self.phase != "HOME":
                self.phase = "HOME"
                self.send_pose(HOME, "return home")
            return
        src, dst = self.orders[self.order_index]
        if self.phase == "WAIT_NAV2":
            self.phase = "SOURCE"
            self.leg = "source"
            self.send_pose(STATIONS[src], f"go to {src}")
        elif self.phase == "AT_SOURCE":
            self.get_logger().warn(f"Reached {src}. PICKUP IS A PLACEHOLDER: crane integration required.")
            self.phase = "DESTINATION"
            self.send_pose(STATIONS[dst], f"go to {dst}")
        elif self.phase == "AT_DESTINATION":
            self.get_logger().warn(f"Reached {dst}. PLACEMENT IS A PLACEHOLDER: crane integration required.")
            self.order_index += 1
            self.phase = "WAIT_NAV2"
        elif self.phase == "HOME_DONE":
            self.get_logger().info("Mission route complete.")
            self.timer.cancel()

    def send_pose(self, pose, description):
        x, y, yaw = pose
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = self.frame_id
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = float(x)
        goal.pose.pose.position.y = float(y)
        q = yaw_quaternion(yaw)
        goal.pose.pose.orientation.x, goal.pose.pose.orientation.y = q[0], q[1]
        goal.pose.pose.orientation.z, goal.pose.pose.orientation.w = q[2], q[3]
        self.busy = True
        self.get_logger().info(f"Sending Nav2 goal: {description}")
        # tick() has already checked server_is_ready(); avoid a blocking wait
        # inside the node's timer callback so callbacks remain responsive.
        future = self.client.send_goal_async(goal)
        future.add_done_callback(lambda f: self.goal_response(f, description))

    def goal_response(self, future, description):
        try:
            handle = future.result()
        except Exception as exc:
            self.busy = False
            self.get_logger().error(f"Failed to send Nav2 goal ({description}): {exc}")
            self.timer.cancel()
            return
        if not handle.accepted:
            self.get_logger().error(f"Nav2 rejected goal: {description}")
            self.busy = False
            return
        result_future = handle.get_result_async()
        result_future.add_done_callback(lambda f: self.goal_result(f, description))

    def goal_result(self, future, description):
        try:
            status = future.result().status
        except Exception as exc:
            self.busy = False
            self.get_logger().error(f"Failed to get Nav2 result ({description}): {exc}")
            self.timer.cancel()
            return
        self.busy = False
        if status != 4:  # action_msgs/GoalStatus.STATUS_SUCCEEDED
            self.get_logger().error(f"Navigation failed ({status}): {description}; stopping mission")
            self.timer.cancel()
            return
        if self.phase == "HOME":
            self.phase = "HOME_DONE"
        elif self.phase == "SOURCE":
            self.phase = "AT_SOURCE"
        elif self.phase == "DESTINATION":
            self.phase = "AT_DESTINATION"
        self.get_logger().info(f"Navigation succeeded: {description}")


def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ValueError) as exc:
        if str(exc):
            node.get_logger().error(str(exc))
    finally:
        node.destroy_node()
        rclpy.shutdown()
