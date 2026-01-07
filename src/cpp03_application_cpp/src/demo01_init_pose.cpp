/* 
  需求：初始化机器人位姿
  topic : /initialpose [geometry_msgs/msg/PoseWithCovarianceStamped]
*/

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"

using geometry_msgs::msg::PoseWithCovarianceStamped;
using namespace std::chrono_literals;

int main(int argc, char const *argv[])
{
  rclcpp::init(argc, argv);

  auto node = rclcpp::Node::make_shared("initial_robot_pose");
  auto init_pose_pub = node->create_publisher<PoseWithCovarianceStamped>("/initialpose", 10);

  rclcpp::sleep_for(1s);

  PoseWithCovarianceStamped init_pose_msg;
  init_pose_msg.header.frame_id = "map";
  init_pose_msg.header.stamp = node->get_clock()->now();

  init_pose_msg.pose.pose.position.x = 0.0;
  init_pose_msg.pose.pose.position.y = 0.0;
  init_pose_msg.pose.pose.orientation.w = 1.0;

  // 设置协方差矩阵为全 0.0
  std::fill(init_pose_msg.pose.covariance.begin(), init_pose_msg.pose.covariance.end(), 0.0);

  init_pose_pub->publish(init_pose_msg);

  RCLCPP_INFO(node->get_logger(), "机器人位姿初始化成功！");
  rclcpp::sleep_for(1s);
  rclcpp::spin(node);

  rclcpp::shutdown();
  return 0;
}
