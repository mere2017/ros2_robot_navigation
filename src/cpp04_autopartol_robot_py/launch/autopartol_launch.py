from launch import LaunchDescription
from launch_ros.actions import Node
#----------获取功能包下 share 目录路径----------
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # 获取默认路径
    autopartol_robot_path = get_package_share_directory('cpp04_autopartol_robot_py')
    default_partol_config_path = autopartol_robot_path + '/config/partol_config.yaml'

    # 加载节点
    action_partol_node = Node(package = 'cpp04_autopartol_robot_py', executable = 'partol_node',
                              output = 'both', parameters = [default_partol_config_path]
    )
    action_speaker_node = Node(package = 'cpp04_autopartol_robot_py', executable = 'speaker')
    
    return LaunchDescription([action_partol_node, action_speaker_node])