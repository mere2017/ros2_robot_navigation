'''
    初始化机器人位姿
    topic : /initialpose [geometry_msgs/msg/PoseWithCovarianceStamped]
'''

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()

    nav = BasicNavigator()  # 是一个节点
    init_pose = PoseStamped()
    # 设置参数
    init_pose.header.frame_id = "map"  # frame_id 要是 map
    init_pose.header.stamp = nav.get_clock().now().to_msg()  # 设置时间戳
    init_pose.pose.position.x = 0.0  # 初始化位置
    init_pose.pose.position.y = 0.0
    init_pose.pose.orientation.w = 1.0  # 初始化朝向，w = 1.0 表示无旋转
    # 传入进行初始化
    nav.setInitialPose(init_pose)
    # 导航的状态转换，需要时间激活
    nav.waitUntilNav2Active()
    rclpy.spin(nav)

    rclpy.shutdown()