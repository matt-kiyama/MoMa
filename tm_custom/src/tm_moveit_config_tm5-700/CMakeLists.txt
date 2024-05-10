cmake_minimum_required(VERSION 3.10.2)
project(tm_moveit_config_tm5-700)

# find dependencies
find_package(ament_cmake REQUIRED)

ament_package()

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})