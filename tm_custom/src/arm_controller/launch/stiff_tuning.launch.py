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
        default_value="ld250_pose",
        description="Odometry topic used by GUI stop/moving status.",
    )

    controller_node_name = LaunchConfiguration("controller_node_name")
    odom_topic = LaunchConfiguration("odom_topic")

    controller_node = Node(
        package="arm_controller",
        executable="controller_refactor",
        name=controller_node_name,
        output="screen",
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
            }
        ],
    )

    return LaunchDescription(
        [
            controller_node_name_arg,
            odom_topic_arg,
            controller_node,
            gui_node,
        ]
    )
