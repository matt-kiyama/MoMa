from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    controller_node_name_arg = DeclareLaunchArgument(
        "controller_node_name",
        default_value="arm_service",
        description="Controller node name used by the GUI parameter client.",
    )
    odom_topic_arg = DeclareLaunchArgument(
        "odom_topic",
        default_value="/platform/odometry",
        description="Odometry topic used by GUI stop/moving status.",
    )
    stop_linear_x_threshold_arg = DeclareLaunchArgument(
        "stop_linear_x_threshold",
        default_value="0.03",
        description="Stopped threshold for odometry linear.x in m/s.",
    )
    stop_linear_y_threshold_arg = DeclareLaunchArgument(
        "stop_linear_y_threshold",
        default_value="0.03",
        description="Stopped threshold for odometry linear.y in m/s.",
    )
    stop_angular_z_threshold_arg = DeclareLaunchArgument(
        "stop_angular_z_threshold",
        default_value="0.05",
        description="Stopped threshold for odometry angular.z in rad/s.",
    )
    stop_hold_time_sec_arg = DeclareLaunchArgument(
        "stop_hold_time_sec",
        default_value="0.25",
        description="How long odometry must stay below stopped thresholds before tuning is allowed.",
    )

    controller_node_name = LaunchConfiguration("controller_node_name")
    odom_topic = LaunchConfiguration("odom_topic")
    stop_linear_x_threshold = LaunchConfiguration("stop_linear_x_threshold")
    stop_linear_y_threshold = LaunchConfiguration("stop_linear_y_threshold")
    stop_angular_z_threshold = LaunchConfiguration("stop_angular_z_threshold")
    stop_hold_time_sec = LaunchConfiguration("stop_hold_time_sec")

    controller_node = Node(
        package="arm_controller",
        executable="controller_refactor",
        name=controller_node_name,
        output="screen",
        parameters=[
            {
                "odom_topic": odom_topic,
                "stop_linear_x_threshold": stop_linear_x_threshold,
                "stop_linear_y_threshold": stop_linear_y_threshold,
                "stop_angular_z_threshold": stop_angular_z_threshold,
                "stop_hold_time_sec": stop_hold_time_sec,
            }
        ],
    )

    gui_node = Node(
        package="arm_controller",
        executable="stiff_tuner_gui",
        name="stiff_param_tuner_gui",
        output="screen",
        parameters=[
            {
                "controller_node_name": controller_node_name,
                "odom_topic": odom_topic,
                "stop_linear_x_threshold": stop_linear_x_threshold,
                "stop_linear_y_threshold": stop_linear_y_threshold,
                "stop_angular_z_threshold": stop_angular_z_threshold,
                "stop_hold_time_sec": stop_hold_time_sec,
            }
        ],
    )

    return LaunchDescription(
        [
            controller_node_name_arg,
            odom_topic_arg,
            stop_linear_x_threshold_arg,
            stop_linear_y_threshold_arg,
            stop_angular_z_threshold_arg,
            stop_hold_time_sec_arg,
            controller_node,
            gui_node,
        ]
    )
