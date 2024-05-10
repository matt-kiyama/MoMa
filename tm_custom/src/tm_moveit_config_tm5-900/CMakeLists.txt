cmake_minimum_required(VERSION 3.10.2)
project(tm_moveit_config_tm5-900)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

ament_package()

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})