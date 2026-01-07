'''
    调用接口进行 路径导航
    action : /follow_waypoints [nav2_msgs/action/FollowWaypoints]
'''

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    nav = BasicNavigator()  # 是一个节点

    # 首先等待导航可用
    nav.waitUntilNav2Active()

    # 设置参数
    goal_pose1 = PoseStamped()
    goal_pose1.header.frame_id = "map"  # frame_id 要是 map
    goal_pose1.header.stamp = nav.get_clock().now().to_msg()  # 设置时间戳
    goal_pose1.pose.position.x = 2.0  # 设置导航至单点位置
    goal_pose1.pose.position.y = 1.0
    goal_pose1.pose.orientation.w = 1.0  # 设置导航至单点朝向
    goal_pose2 = PoseStamped()
    goal_pose2.header.frame_id = "map"  # frame_id 要是 map
    goal_pose2.header.stamp = nav.get_clock().now().to_msg()  # 设置时间戳
    goal_pose2.pose.position.x = -3.0  # 设置导航至单点位置
    goal_pose2.pose.position.y = -2.5
    goal_pose2.pose.orientation.w = 1.0  # 设置导航至单点朝向
    goal_pose3 = PoseStamped()
    goal_pose3.header.frame_id = "map"  # frame_id 要是 map
    goal_pose3.header.stamp = nav.get_clock().now().to_msg()  # 设置时间戳
    goal_pose3.pose.position.x = 0.0  # 设置导航至单点位置
    goal_pose3.pose.position.y = 0.0
    goal_pose3.pose.orientation.w = 1.0  # 设置导航至单点朝向

    # 创建数组，用于存储多个路径点
    goal_poses = []
    goal_poses.append(goal_pose1)
    goal_poses.append(goal_pose2)
    goal_poses.append(goal_pose3)

    # 传入进行 路径导航
    nav.followWaypoints(goal_poses)
    # 等待运行完成
    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        nav.get_logger().info(f'路点编号: {feedback.current_waypoint}')

    result = nav.getResult()
    nav.get_logger().info(f'导航结果: {result}')