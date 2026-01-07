/* 
    需求：调用接口进行 单点导航
    action : /navigate_to_pose [nav2_msgs/action/NavigateToPose]
*/

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_msgs/action/navigate_to_pose.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

using namespace std::chrono_literals;
using nav2_msgs::action::NavigateToPose;
using GoalHandleNavigateToPose = rclcpp_action::ClientGoalHandle<NavigateToPose>;

class SinglePointNavigator : public rclcpp::Node
{
public:
  SinglePointNavigator() : Node("nav_to_pose")
  {
    // 创建action客户端
    action_client_ = rclcpp_action::create_client<NavigateToPose>(this, "navigate_to_pose");
  }

  void sendGoal()
  {
    if (!action_client_->wait_for_action_server(10s))
    {
      RCLCPP_ERROR(this->get_logger(), "服务端未响应！");
      return;
    }

    auto goal_msg = NavigateToPose::Goal();
    // 设置参数
    goal_msg.pose.header.frame_id = "map";
    goal_msg.pose.header.stamp = this->now();
    goal_msg.pose.pose.position.x = 2.0;
    goal_msg.pose.pose.position.y = 1.0;
    goal_msg.pose.pose.orientation.w = 1.0;
    auto send_goal_options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();

    // 发送坐标，进行导航
    auto future_goal_handle = action_client_->async_send_goal(goal_msg, send_goal_options);
  }

private:
  rclcpp_action::Client<NavigateToPose>::SharedPtr action_client_;

};

int main(int argc, char const *argv[])
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<SinglePointNavigator>();

  // 等待，确保节点完全初始化
  rclcpp::sleep_for(2s);
  // 发送导航目标
  node->sendGoal();
  rclcpp::spin(node);

  rclcpp::shutdown();
  return 0;
}
