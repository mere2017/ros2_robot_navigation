from launch import LaunchDescription
from launch_ros.actions import Node
#----------封装终端指令相关类----------
from launch.actions import ExecuteProcess
#----------事件相关----------", 
from launch.event_handlers import OnProcessExit
from launch.actions import RegisterEventHandler
#----------参数声明与获取----------
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
#----------获取功能包下 share 目录路径----------
from ament_index_python.packages import get_package_share_directory
import os
#----------launch 文件包含相关----------
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
#----------xacro 命令----------
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command

""" 
    需求：加载 xacro 文件和 world 文件，并在 gazebo 中显示地图 + 机器人模型
    核心：
        1. 加载 xacro + world 文件
        2. 启动 gazebo
        3. 在 gazebo 中添加机器人模型
"""

def generate_launch_description():
    # 声明 xacro 路径
    xacro_path = DeclareLaunchArgument(name = "xacro_path",
                                        default_value = get_package_share_directory("cpp01_nav") + "/urdf/car.urdf.xacro")
    # 声明 world 路径
    gazebo_world_path = DeclareLaunchArgument(name  = "world_path",
                                              default_value = get_package_share_directory("cpp01_nav") + "/world/BigHouse.world")
    
    # 加载 xacro 文件
    param_value = ParameterValue(Command(["xacro ", LaunchConfiguration("xacro_path")]))
                                                                 
    robot_state_pub = Node(package = "robot_state_publisher", executable = "robot_state_publisher",
                           parameters = [{'robot_description': param_value, "use_sim_time": True}])
    

    # 添加 joint_state_publisher 节点（当机器人有 活动关节/非固定关节 时必须包含该节点）
    joint_state_pub = Node(package = "joint_state_publisher", executable = "joint_state_publisher",
                           parameters = [{"use_sim_time": True,  # 同步 Gazebo 仿真时间
                                        "rate": 30.0}]  # 发布频率
                           )
    
    # 启动 rviz2 节点
    rviz2 = Node(package = "rviz2", executable = "rviz2",
                 arguments = ["-d", get_package_share_directory("cpp01_nav") + "/rviz/car.rviz"]
                )

    
    # 启动 gazebo
    action_launch_gazebo = IncludeLaunchDescription(
        launch_description_source = PythonLaunchDescriptionSource(
            launch_file_path = os.path.join(get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py")
            ),
        # 设置所包含 launch 文件的参数
        launch_arguments = [("world", LaunchConfiguration("world_path")), ("verbose", "true")]
    )
    
    # 在 gazebo 中加载 机器人模型，将 urdf 格式转换为 gazebo 的 rdf 格式
    action_spawn_entity = Node(package = "gazebo_ros", executable = "spawn_entity.py",
                               arguments = ['-topic', 'robot_description',
                                            '-entity', 'car'])
    
    # 加载并激活 car_joint_state_broadcaster，并要在 gazebo 加载 robot 之后，才能启动
    action_load_joint_state_controller = ExecuteProcess(
        cmd = 'ros2 control load_controller car_joint_state_broadcaster --set-state active'.split(' '),
        output = "both",
        shell = True
    )
    # 加载并激活力控 car_effort_controller，并在上一个 controller 之后依次启动
    action_load_effort_controller = ExecuteProcess(
        cmd = 'ros2 control load_controller car_effort_controller --set-state active'.split(' '),
        output = "both",
        shell = True
    )

    # 加载并激活两轮差速控制器 car_diff_drive_controller，需要关掉 力控、在上一个 controller 之后依次启动
    action_load_diff_drive_controller = ExecuteProcess(
        cmd = 'ros2 control load_controller car_diff_drive_controller --set-state active'.split(' '),
        output = "both",
        shell = True
    )

    return LaunchDescription([xacro_path, 
                              gazebo_world_path, 
                              robot_state_pub, 
                            #   joint_state_pub,
                            #   rviz2,
                              action_launch_gazebo,
                              action_spawn_entity,
                              # 加载并激活 car_joint_state_broadcaster，要求在 gazebo 加载 robot 之后启动
                              RegisterEventHandler(
                                  event_handler = OnProcessExit(
                                      target_action = action_spawn_entity,
                                      on_exit = [action_load_joint_state_controller]
                                  )
                              ),
                              # 加载并激活力控 car_effort_controller，并在上一个 controller 之后依次启动
                            #   RegisterEventHandler(
                            #       event_handler = OnProcessExit(
                            #           target_action = action_load_joint_state_controller,
                            #           on_exit = [action_load_effort_controller]
                            #       )
                            #   )

                              # 加载并激活两轮差速控制器 car_diff_drive_controller，需要关掉 力控、在上一个 controller 之后依次启动
                              RegisterEventHandler(
                                  event_handler = OnProcessExit(
                                      target_action = action_load_joint_state_controller,
                                      on_exit = [action_load_diff_drive_controller]
                                  )
                              )
                            ])