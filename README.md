# Factory Robot ROS 2 + Gazebo + Nav2 (portfolio project)

A staged ROS 2 portfolio project for an indoor material-handling robot. It contains a ROS 2 mission sequencer, camera topic subscriber, fail-safe ultrasonic range monitor, starter robot description, factory world, and Nav2 parameter template. Target stack:
- Ubuntu 24.04 / ROS 2 Jazzy
- Gazebo Harmonic via `ros_gz`
- Nav2 for base navigation
- Camera/OpenCV perception
- Ultrasonic safety guard
- Mission manager using Nav2 actions

**Status: early integration / portfolio prototype.** Offline Python syntax and project-file checks are included. This repository is not yet a verified turnkey simulation: ROS/Gazebo/Nav2 end-to-end execution has not been tested in your Distrobox, and the launch file intentionally does not pretend to start an unconfigured Nav2/Gazebo stack. You must adapt the Gazebo plugins, topic names, robot model, controllers, transforms and Nav2 parameters to your installed Gazebo/ROS packages. The included simple model is a differential-drive placeholder; it does not implement physically accurate tank treads or the crane yet.

## Repository layout

- `factory_robot/mission_manager.py`: sends Nav2 goals for station-to-station orders.
- `factory_robot/ultrasonic_guard.py`: publishes an obstacle flag from `sensor_msgs/Range`.
- `factory_robot/camera_perception.py`: camera subscriber / OpenCV starter.
- `launch/factory.launch.py`: launches the ROS nodes (Gazebo/Nav2 are separate until model-specific config is finished).
- `urdf/factory_robot.urdf.xacro`: starter robot model with camera and ultrasonic frames.
- `worlds/factory.sdf`: simple factory world placeholder.
- `config/nav2_params.yaml`: starter Nav2 configuration template.
- `scripts/check_topics.sh`: basic ROS graph checks.

## 1. Build inside your ROS Distrobox

Open the Distrobox terminal where ROS 2 is installed. Confirm:
```bash
echo "$ROS_DISTRO"
ros2 --help
```
For the default instructions below, `ROS_DISTRO` should be `jazzy`. If yours is `humble`, `iron`, `rolling`, or another distro, do not blindly use Jazzy package names; adapt dependencies.

Put this folder inside your distrobox-visible home directory, or clone the repository there. Then:
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
cd ~/factory_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```
If this folder is not already at `~/factory_ws/src/factory_robot`, create the workspace and copy it there:
```bash
mkdir -p ~/factory_ws/src
cp -a /path/to/factory_robot_ros2 ~/factory_ws/src/factory_robot
```

## 2. Run checks first
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/factory_ws/install/setup.bash
ros2 topic list
```
Check the actual topics published by your Gazebo plugins:
```bash
ros2 topic list | grep -E 'camera|image|range|scan|odom|cmd_vel|joint'
```
Topic names in this project are examples and may need remapping.

## 3. Start nodes
```bash
ros2 launch factory_robot factory.launch.py
```
This launches the mission manager, camera subscriber and ultrasonic guard. It does not yet launch a configured Gazebo simulation or Nav2 bringup automatically; those must be integrated after confirming your installed versions, Gazebo plugins, map and robot model.

Example order:
```bash
ros2 run factory_robot mission_manager --ros-args -p orders:="['S1>S3','S2>S4','S3>S1']"
```

## 4. Safety note
The ultrasonic node publishes `/safety/obstacle`; it does not itself guarantee the base stops. Connect this signal to a safety controller or velocity-command gate that can override Nav2 output. Use physical emergency stop and conservative speed limits on hardware. A single ultrasonic sensor is not a 360-degree lidar.

## 5. Next integration steps
1. Confirm ROS distro and `ros_gz` / Gazebo versions.
2. Make the URDF compatible with your installed `ros2_control` and Gazebo system plugins.
3. Add differential-drive or tracked-drive plugin/controller and verify `/cmd_vel` + `/odom`.
4. Publish `map -> odom -> base_link` transforms and configure localization.
5. Add a real map and tune Nav2 global/local costmaps and footprint.
6. Verify camera image topic and calibrate the camera; implement station-tag detection.
7. Integrate ultrasonic readings into a safety gate and optionally a Nav2 range layer.
8. Add crane joints/controllers and magnet attach/detach only after navigation works.

## Troubleshooting
- `Package 'factory_robot' not found`: source `install/setup.bash` after building.
- `ros2 launch` cannot find launch file: ensure `setup.py` installs `launch/`, rebuild.
- No image/range messages: inspect `ros2 topic list`, Gazebo bridge configuration and plugin topic names.
- Nav2 reports missing transforms: inspect `ros2 run tf2_tools view_frames` and ensure odometry + TF are being published.
- Robot doesn't move: check `/cmd_vel` subscriber, drive plugin/controller, QoS and topic remaps.


## Offline checks (no ROS needed)
From the repository root:
```bash
python3 -m compileall -q factory_robot tests
python3 -m unittest discover -s tests -v
```
These checks verify Python syntax and basic project-file validity. They do **not** validate ROS imports, Nav2 behavior, Gazebo plugins, transforms, sensor simulation, or robot motion. GitHub Actions runs these same checks.

## Current known limitations
- `worlds/factory.sdf` is a floor-and-light starter world; stations, shelving, and obstacles still need models.
- `urdf/factory_robot.urdf.xacro` defines placeholder geometry and sensor frames, but does not yet load a drive plugin, camera plugin, ultrasonic plugin, `ros2_control`, or crane joints. Therefore it will not move or publish sensor topics in Gazebo by itself.
- `config/nav2_params.yaml` is a template, not a complete Nav2 bringup. A map, localization, controller servers, lifecycle setup, and correct TF/odometry/sensor topics are required. It currently configures a LaserScan obstacle layer; a single `sensor_msgs/Range` ultrasonic sensor is not a replacement for a 360-degree scan.
- The mission manager sequences Nav2 goals only. Pick/place actions are logged placeholders; crane controllers and magnet/gripper integration remain to be implemented.
- The ultrasonic guard publishes `/safety/obstacle` and fails safe when range data is missing/stale. It does not physically stop the robot unless a velocity safety gate subscribes to that signal.
- Real hardware must have an independent emergency stop and conservative speed limits.
