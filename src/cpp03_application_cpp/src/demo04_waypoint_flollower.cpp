/* 
    需求：调用接口进行 路径导航
    action : /follow_waypoints [nav2_msgs/action/FollowWaypoints]
*/

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_msgs/action/follow_waypoints.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

using namespace std::chrono_literals;
using nav2_msgs::action::FollowWaypoints;
using GoalHandleFollowWaypoints = rclcpp_action::ClientGoalHandle<FollowWaypoints>;

class WaypointNavigator  : public rclcpp::Node
{
public:
  WaypointNavigator () : Node("waypoint_navigator")
  {
    // 创建action客户端
    action_client_ = rclcpp_action::create_client<FollowWaypoints>(this, "follow_waypoints");
  }

  void sendGoalpoints()
  {
    if (!action_client_->wait_for_action_server(10s))
    {
      RCLCPP_ERROR(this->get_logger(), "服务端未响应！");
      return;
    }

    RCLCPP_INFO(this->get_logger(), "Action服务器已连接");

    // 创建目标消息
    auto goal_msg = FollowWaypoints::Goal();
    // 创建多个路点
    geometry_msgs::msg::PoseStamped pose1, pose2, pose3;
    // 设置参数
    pose1.header.frame_id = "map";
    pose1.header.stamp = this->now();
    pose1.pose.position.x = 2.0;
    pose1.pose.position.y = 1.0;
    pose1.pose.orientation.w = 1.0;

    pose2.header.frame_id = "map";
    pose2.header.stamp = this->now();
    pose2.pose.position.x = -4.0;
    pose2.pose.position.y = -3.5;
    pose2.pose.orientation.w = 1.0;

    pose3.header.frame_id = "map";
    pose3.header.stamp = this->now();
    pose3.pose.position.x = 0.0;
    pose3.pose.position.y = 0.0;
    pose3.pose.orientation.w = 1.0;
    // 添加到数组
    goal_msg.poses.push_back(pose1);
    goal_msg.poses.push_back(pose2);
    goal_msg.poses.push_back(pose3);

    // 设置发送选项
    auto send_goal_options = rclcpp_action::Client<FollowWaypoints>::SendGoalOptions();
    // 设置反馈回调
    send_goal_options.feedback_callback = 
        [this](GoalHandleFollowWaypoints::SharedPtr,
                const std::shared_ptr<const FollowWaypoints::Feedback> feedback) {
            RCLCPP_INFO(this->get_logger(), "当前路点编号: %d", 
                        feedback->current_waypoint);
        };

    // 发送坐标，进行导航
    auto future_goal_handle = action_client_->async_send_goal(goal_msg, send_goal_options);
  }

private:
  rclcpp_action::Client<FollowWaypoints>::SharedPtr action_client_;
};


int main(int argc, char const *argv[])
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<WaypointNavigator >();

  // 等待，确保节点完全初始化
  rclcpp::sleep_for(2s);
  // 发送导航目标
  node->sendGoalpoints();
  rclcpp::spin(node);

  rclcpp::shutdown();
  return 0;
}
