from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package="factory_robot", executable="mission_manager",
             name="mission_manager", output="screen"),
        Node(package="factory_robot", executable="ultrasonic_guard",
             name="ultrasonic_guard", output="screen"),
        Node(package="factory_robot", executable="camera_perception",
             name="camera_perception", output="screen"),
    ])
