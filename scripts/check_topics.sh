#!/usr/bin/env bash
set -e
echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
ros2 topic list
echo
echo "Potentially relevant topics:"
ros2 topic list | grep -E 'camera|image|range|scan|odom|cmd_vel|joint' || true
