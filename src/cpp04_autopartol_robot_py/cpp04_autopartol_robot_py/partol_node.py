'''
    需求：实现机器人定点循环 导航巡检
         加入语音播报功能
         导航到单点后，订阅图像并保存记录
'''

import rclpy
import rclpy.time
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from tf2_ros import TransformListener, Buffer   # 坐标监听器
from tf_transformations import euler_from_quaternion, quaternion_from_euler    # 四元数转欧拉角、欧拉教转四元数函数
from autopartol_interfaces.srv import SpeechText    # 导入消息接口，用于创建语音客户端
from sensor_msgs.msg import Image   # 导入消息接口，用于创建摄像机图像订阅方
from cv_bridge import CvBridge  # 用于转换图像格式
import cv2  # 用于保存图像

class PartolNode(BasicNavigator):   # BasicNavigator 本身就是继承 Node，所以编写的类也是继承 Node 的
    # 初始化
    def __init__(self, node_name = 'partol_robot'):
        # 调用父类，初始化节点的名字
        super().__init__(node_name)
        # 声明相关参数
        self.declare_parameter('initial_point', [0.0, 0.0, 0.0])    # 初始化位姿：x、y、w
        self.declare_parameter('target_points', [0.0, 0.0, 0.0, 1.0, 1.0, 1.57])    # 目标点(个数为3的倍数)
        self.initial_point_ = self.get_parameter('initial_point').value     # 获取参数值
        self.target_points_ = self.get_parameter('target_points').value
        self.buffer = Buffer()  # 用于监听机器人的坐标
        self.listener = TransformListener(self.buffer, self)
        self.speech_client_ = self.create_client(SpeechText, 'speech_text')  # 创建语音客户端
        self.declare_parameter('image_save_path', '')   # 摄像机图像保存路径，默认空即当前目录
        self.image_save_path_ = self.get_parameter('image_save_path').value
        self.cv_bridge_ = CvBridge()
        self.latest_img_ = None     # 创建成员变量，实时保存最新的图像
        self.img_sub_ = self.create_subscription(Image, '/camera_sensor/image_raw', self.img_callback, 1)   # 创建摄像机图像订阅方

    def get_pose_by_xyyaw(self, x, y, yaw):
        '''
            通过x、y、yaw值，返回一个 PoseStamped 对象，用于后面的数据输入
        '''
        pose = PoseStamped()    # 首先定义一个 PoseStamped 对象
        pose.header.frame_id = 'map'    # 赋值
        pose.pose.position.x = x
        pose.pose.position.y = y
        quat = quaternion_from_euler(0, 0, yaw)  # 定义一个四元数，返回顺序是 x、y、z、w
        pose.pose.orientation.x = quat[0]
        pose.pose.orientation.y = quat[1]
        pose.pose.orientation.z = quat[2]
        pose.pose.orientation.w = quat[3]
        return pose

    def init_robot_pose(self):
        '''
            初始化机器人的位姿
        '''
        self.initial_point_ = self.get_parameter('initial_point').value     # 获取参数值
        #  将参数值转换为要用的 PoseStamped 对象
        init_pose = self.get_pose_by_xyyaw(self.initial_point_[0], self.initial_point_[1],
                                           self.initial_point_[2])
        self.setInitialPose(init_pose)   # 传参、初始化位姿
        self.waitUntilNav2Active()  # 等待导航可用


    def get_target_points(self):
        '''
            通过参数值，获取目标点的集合
        '''
        points = [] # 首先定义一个目标点的集合
        self.target_points_ = self.get_parameter('target_points').value # 获取参数值
        for index in range(int(len(self.target_points_)/3)):
            x = self.target_points_[index * 3]
            y = self.target_points_[index * 3 + 1]
            yaw = self.target_points_[index * 3 + 2]
            points.append([x, y, yaw])
            self.get_logger().info(f"获取到目标点{index} -> {x}, {y}, {yaw}")
        return points

    def nav_to_pose(self, target_point):
        '''
            导航到目标点
        '''
        self.goToPose(target_point) # 目标点传参、导航到目标点
        while not self.isTaskComplete():
            feedback = self.getFeedback()
            self.get_logger().info(f"剩余距离：{feedback.distance_remaining}")
        result = self.getResult()
        self.get_logger().info(f"导航结果：{result}")

    def get_current_pose(self):
        '''
            获取机器人当前的位姿：使用 tf
        '''
        while rclpy.ok():
            try:
                result = self.buffer.lookup_transform('map', 'base_footprint', 
                            rclpy.time.Time(seconds=0.0), rclpy.time.Duration(seconds=1.0))
                transform = result.transform
                rotation_euler = euler_from_quaternion([
                    transform.rotation.x,
                    transform.rotation.y,
                    transform.rotation.z,
                    transform.rotation.w])
                self.get_logger().info(f'平移:{transform.translation}\n旋转欧拉角:{rotation_euler}')
                return transform    # 要用到 transform 进行语音播放
            except Exception as e:
                self.get_logger().warn(f'不能够获取坐标变换，原因: {str(e)}')

    def speech_text(self, text):
        '''
            调用服务，合成语音
        '''
        while not self.speech_client_.wait_for_service(timeout_sec = 1.0):
            self.get_logger().info('语音合成服务端连接，等待中...')
        
        request = SpeechText.Request()  # 创建请求
        request.text = text     # 对语音内容（消息接口）进行赋值
        future = self.speech_client_.call_async(request)    # 异步发送请求
        rclpy.spin_until_future_complete(self, future)    # 等待服务端完成
        if future.result() is not None:     # 语音合成有结果
            response = future.result()  # 获取结果
            if response.result == True:
                self.get_logger().info(f'语音合成成功：{text}')
            else:
                self.get_logger().warn(f'语音合成失败：{text}')
        else:
            self.get_logger().error('语音合成服务响应失败！')

    def img_callback(self, msg):
        '''
            图像订阅回调函数
        '''
        self.latest_img_ = msg  # 更新最新图像

    def record_img(self):
        '''
            保存图像：将 latest_img_ 保存为 opencv 格式的图像
        '''
        if self.latest_img_ is not None:    # 要非空才能保存
            pose = self.get_current_pose()  # 获取机器人当前位置
            cv_image = self.cv_bridge_.imgmsg_to_cv2(self.latest_img_)  # 转换成 opencv 的格式
            # 保存图像
            cv2.imwrite(
                f'{self.image_save_path_}img_{pose.translation.x:3.2f}_{pose.translation.y:3.2f}.png',    # 保存路径和名字
                cv_image    # 需要保存的图像
            )


def main():
    rclpy.init()

    partol = PartolNode()  # 创建节点
    # rclpy.spin(partol)    # 为生成参数，填写 partol_config.yaml 文件才运行，正式运行中需要注释掉
    partol.speech_text('正在准备初始化...')

    partol.init_robot_pose()    # 先初始化
    partol.speech_text('初始化已完成！')

    while rclpy.ok():
        points = partol.get_target_points() # 获取导航所需目标点
        for point in points:
            x, y, yaw = point[0], point[1], point[2]
            target_pose = partol.get_pose_by_xyyaw(x, y, yaw)   # 转换成要用的 PoseStamped 对象
            partol.speech_text(f'正在准备前往{x},{y}目标点...')
            partol.nav_to_pose(target_pose) # 进行导航
            partol.speech_text(f'已经到达{x},{y}目标点，正在准备记录图像...')
            partol.record_img() # 记录图像
            partol.speech_text('图像记录已完成！')
            
    # 不需要使用 spin，因为 BasicNavigator 里面包含了

    rclpy.shutdown()

    # 在 setup.py 配置文件中添加：'console_scripts': ['partol_node = cpp04_autopartol_robot_py.partol_node:main',],
    # 调用时传参：
    #    ros2 run cpp04_autopartol_robot_py partol_node --ros-args --params-file /home/mere/ws03_navigation/install/cpp04_autopartol_robot_py/share/cpp04_autopartol_robot_py/config/partol_config.yaml