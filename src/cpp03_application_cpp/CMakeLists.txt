cmake_minimum_required(VERSION 3.8)
project(cpp03_application_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(nav2_msgs REQUIRED)

add_executable(demo01_init_pose src/demo01_init_pose.cpp)
add_executable(demo02_get_pose src/demo02_get_pose.cpp)
add_executable(demo03_nav_to_pose src/demo03_nav_to_pose.cpp)
add_executable(demo04_waypoint_flollower src/demo04_waypoint_flollower.cpp)

target_include_directories(demo01_init_pose PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
target_compile_features(demo01_init_pose PUBLIC c_std_99 cxx_std_17)  # Require C99 and C++17
ament_target_dependencies(
  demo01_init_pose
  "rclcpp"
  "geometry_msgs"
)
ament_target_dependencies(
  demo02_get_pose
  "rclcpp"
  "geometry_msgs"
  "tf2"
  "tf2_ros"
)
ament_target_dependencies(
  demo03_nav_to_pose
  "rclcpp"
  "geometry_msgs"
  "rclcpp_action"
  "nav2_msgs"
)
ament_target_dependencies(
  demo04_waypoint_flollower
  "rclcpp"
  "geometry_msgs"
  "rclcpp_action"
  "nav2_msgs"
)

install(TARGETS 
  demo01_init_pose
  demo02_get_pose
  demo03_nav_to_pose
  demo04_waypoint_flollower
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
