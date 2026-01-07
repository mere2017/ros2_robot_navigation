'''
    需求：自定义 service 消息接口，并创建语音服务端
'''

import rclpy
from rclpy.node import Node
from autopartol_interfaces.srv import SpeechText    # 导入消息接口，用于创建语音服务端
import espeakng     # 语音合成库

class Speaker(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        # 创建语音服务端
        self.speech_service_ = self.create_service(SpeechText, 'speech_text',
                                                   self.speech_text_callback)
        self.speaker_ = espeakng.Speaker()  # 设置一个 speaker
        self.speaker_.voice = 'zh'    # 设置声音为中文
        
    def speech_text_callback(self, request, response):
        '''
            语音回调函数
        '''
        self.get_logger().info(f'正在准备朗读{request.text}')
        # 启动朗读
        self.speaker_.say(request.text)     # 说消息接口里面的 text 内容
        self.speaker_.wait()    # 等待说完
        response.result = True  # 给消息接口的 result 赋值，并作为响应返回
        return response
    

def main():
    rclpy.init()

    node = Speaker('speaker')
    rclpy.spin(node)

    rclpy.shutdown()