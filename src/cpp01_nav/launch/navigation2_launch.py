from launch import LaunchDescription
from launch_ros.actions import Node
#----------参数声明与获取----------
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
#----------launch 文件包含相关----------
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
#----------获取功能包下 share 目录路径----------
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取与拼接默认路径
    car_navigation2_dir = get_package_share_directory(
        'cpp01_nav')
    # 下面两项是所安装的 nav2_bringup 的配置文件
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    rviz_config_dir = os.path.join(
        nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')
    
    # 创建 Launch 配置
    use_sim_time = LaunchConfiguration(
        'use_sim_time', default='true')
    map_yaml_path = LaunchConfiguration(
        'map', default=os.path.join(car_navigation2_dir, 'maps', 'room.yaml'))
    nav2_param_path = LaunchConfiguration(
        'params_file', default=os.path.join(car_navigation2_dir, 'config', 'nav2_params.yaml'))

    return LaunchDescription([
        # 声明新的 Launch 参数
        DeclareLaunchArgument('use_sim_time', default_value=use_sim_time,
                                             description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument('map', default_value=map_yaml_path,
                                             description='Full path to map file to load'),
        DeclareLaunchArgument('params_file', default_value=nav2_param_path,
                                             description='Full path to param file to load'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [nav2_bringup_dir, '/launch', '/bringup_launch.py']),
            # 使用 Launch 参数替换原有参数
            launch_arguments={
                'map': map_yaml_path,
                'use_sim_time': use_sim_time,
                'params_file': nav2_param_path}.items(),
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'),
    ])