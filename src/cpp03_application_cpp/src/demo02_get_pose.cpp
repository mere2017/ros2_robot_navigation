/*
    需求:利用 tf 实时获取机器人位姿
*/

#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"

using namespace std::chrono_literals;

// 自定义节点类
class GetPose : public rclcpp::Node
{
public:
    GetPose() : Node("get_pose_node")
    {
      // 创建一个缓存对象（由于需要保存多个坐标系相对关系，然后融合成一个坐标树。因此需要一个缓存来存储所有坐标系）
      buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());  // this->get_clock()获取时钟信息
      // 创建一个监听器，绑定缓存对象（会将所有广播器广播的数据写入缓存）
      listener_ = std::make_shared<tf2_ros::TransformListener>(*buffer_, this);
      // 创建一个定时器，循环实现坐标系的转换
      timer_ = this->create_wall_timer(1s, std::bind(&GetPose::on_timer_callback, this));
    }

private:
    std::unique_ptr<tf2_ros::Buffer> buffer_;
    std::shared_ptr<tf2_ros::TransformListener> listener_;
    rclcpp::TimerBase::SharedPtr timer_;

    // 定时器回调函数，实现坐标系的转换
    void on_timer_callback()
    {
      // 进行异常处理：当 buffer_ 里面还没有缓存到所需要的坐标系数据时，坐标系的转换就会报异常
      try
      {
        // 实现坐标系转换
        // 参数1：父级坐标系；参数2：子级坐标系；参数3：转换的时间点，选用最新时刻 tf2::TimePointZero；参数4：超时时间(1s)
        auto trans = buffer_->lookupTransform("map", "base_footprint", tf2::TimePointZero, tf2::durationFromSec(1.0));

        RCLCPP_INFO(this->get_logger(),
            "\n--------机器人实时坐标信息--------"
            "\n平移:(%.2f, %.2f, %.2f)  \n旋转四元数:(%.2f, %.2f, %.2f, %.2f)",
            trans.transform.translation.x,
            trans.transform.translation.y,
            trans.transform.translation.z,
            trans.transform.rotation.x,
            trans.transform.rotation.y,
            trans.transform.rotation.z,
            trans.transform.rotation.w
          );
      }
      catch(const tf2::LookupException& e)
      {
        RCLCPP_WARN(this->get_logger(), "获取机器人坐标失败！，异常提示：%s", e.what());
      }
    }
};


int main(int argc, char const *argv[])
{
    // 初始化
    rclcpp::init(argc, argv);

    // 调用spin函数,传入节点对象指针
    rclcpp::spin(std::make_shared<GetPose>());

    // 释放资源
    rclcpp::shutdown();

    return 0;
}