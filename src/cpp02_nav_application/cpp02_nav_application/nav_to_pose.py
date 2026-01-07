'''
    调用接口进行 单点导航
    action : /navigate_to_pose [nav2_msgs/action/NavigateToPose]
'''

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    nav = BasicNavigator()  # 是一个节点

    # 首先等待导航可用
    nav.waitUntilNav2Active()

    goal_pose = PoseStamped()
    # 设置参数
    goal_pose.header.frame_id = "map"  # frame_id 要是 map
    goal_pose.header.stamp = nav.get_clock().now().to_msg()  # 设置时间戳
    goal_pose.pose.position.x = 2.0  # 设置导航至单点位置
    goal_pose.pose.position.y = 1.0
    goal_pose.pose.orientation.w = 1.0  # 设置导航至单点朝向
    # 传入进行 单点导航
    nav.goToPose(goal_pose)
    # 等待运行完成
    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        nav.get_logger().info(f'剩余距离: {feedback.distance_remaining}')

    result = nav.getResult()
    nav.get_logger().info(f'导航结果: {result}')