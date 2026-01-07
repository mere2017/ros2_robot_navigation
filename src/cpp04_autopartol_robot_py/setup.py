from setuptools import find_packages, setup
from glob import glob

package_name = 'cpp04_autopartol_robot_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 添加配置文件路径
        ('share/' + package_name + "/config", ['config/partol_config.yaml']),
        # 添加 launch 文件路径
        ('share/' + package_name + '/launch', glob('launch/*_launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mere',
    maintainer_email='userEmail',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # 添加 节点文件
            'partol_node = cpp04_autopartol_robot_py.partol_node:main',
            'speaker = cpp04_autopartol_robot_py.speaker:main',
        ],
    },
)
