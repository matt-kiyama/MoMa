# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/rslomron/tm_custom/src/ui_for_debug_and_demo

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/rslomron/tm_custom/build/ui_for_debug_and_demo

# Include any dependencies generated for this target.
include CMakeFiles/robot_ui.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/robot_ui.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/robot_ui.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/robot_ui.dir/flags.make

ui_tm_ros_driver_windows.h: /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/tm_ros_driver_windows.ui
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold --progress-dir=/home/rslomron/tm_custom/build/ui_for_debug_and_demo/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Generating ui_tm_ros_driver_windows.h"
	/usr/lib/qt5/bin/uic -o /home/rslomron/tm_custom/build/ui_for_debug_and_demo/ui_tm_ros_driver_windows.h /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/tm_ros_driver_windows.ui

CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o: CMakeFiles/robot_ui.dir/flags.make
CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o: robot_ui_autogen/mocs_compilation.cpp
CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o: CMakeFiles/robot_ui.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/rslomron/tm_custom/build/ui_for_debug_and_demo/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o -MF CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o.d -o CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o -c /home/rslomron/tm_custom/build/ui_for_debug_and_demo/robot_ui_autogen/mocs_compilation.cpp

CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/rslomron/tm_custom/build/ui_for_debug_and_demo/robot_ui_autogen/mocs_compilation.cpp > CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.i

CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/rslomron/tm_custom/build/ui_for_debug_and_demo/robot_ui_autogen/mocs_compilation.cpp -o CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.s

CMakeFiles/robot_ui.dir/src/main.cpp.o: CMakeFiles/robot_ui.dir/flags.make
CMakeFiles/robot_ui.dir/src/main.cpp.o: /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/main.cpp
CMakeFiles/robot_ui.dir/src/main.cpp.o: CMakeFiles/robot_ui.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/rslomron/tm_custom/build/ui_for_debug_and_demo/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object CMakeFiles/robot_ui.dir/src/main.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/robot_ui.dir/src/main.cpp.o -MF CMakeFiles/robot_ui.dir/src/main.cpp.o.d -o CMakeFiles/robot_ui.dir/src/main.cpp.o -c /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/main.cpp

CMakeFiles/robot_ui.dir/src/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/robot_ui.dir/src/main.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/main.cpp > CMakeFiles/robot_ui.dir/src/main.cpp.i

CMakeFiles/robot_ui.dir/src/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/robot_ui.dir/src/main.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/main.cpp -o CMakeFiles/robot_ui.dir/src/main.cpp.s

CMakeFiles/robot_ui.dir/src/ros_page.cpp.o: CMakeFiles/robot_ui.dir/flags.make
CMakeFiles/robot_ui.dir/src/ros_page.cpp.o: /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/ros_page.cpp
CMakeFiles/robot_ui.dir/src/ros_page.cpp.o: CMakeFiles/robot_ui.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/rslomron/tm_custom/build/ui_for_debug_and_demo/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Building CXX object CMakeFiles/robot_ui.dir/src/ros_page.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/robot_ui.dir/src/ros_page.cpp.o -MF CMakeFiles/robot_ui.dir/src/ros_page.cpp.o.d -o CMakeFiles/robot_ui.dir/src/ros_page.cpp.o -c /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/ros_page.cpp

CMakeFiles/robot_ui.dir/src/ros_page.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/robot_ui.dir/src/ros_page.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/ros_page.cpp > CMakeFiles/robot_ui.dir/src/ros_page.cpp.i

CMakeFiles/robot_ui.dir/src/ros_page.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/robot_ui.dir/src/ros_page.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/ros_page.cpp -o CMakeFiles/robot_ui.dir/src/ros_page.cpp.s

CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o: CMakeFiles/robot_ui.dir/flags.make
CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o: /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/tm_ros_driver_windows.cpp
CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o: CMakeFiles/robot_ui.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/rslomron/tm_custom/build/ui_for_debug_and_demo/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "Building CXX object CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o -MF CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o.d -o CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o -c /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/tm_ros_driver_windows.cpp

CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/tm_ros_driver_windows.cpp > CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.i

CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/rslomron/tm_custom/src/ui_for_debug_and_demo/src/tm_ros_driver_windows.cpp -o CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.s

# Object files for target robot_ui
robot_ui_OBJECTS = \
"CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o" \
"CMakeFiles/robot_ui.dir/src/main.cpp.o" \
"CMakeFiles/robot_ui.dir/src/ros_page.cpp.o" \
"CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o"

# External object files for target robot_ui
robot_ui_EXTERNAL_OBJECTS =

robot_ui: CMakeFiles/robot_ui.dir/robot_ui_autogen/mocs_compilation.cpp.o
robot_ui: CMakeFiles/robot_ui.dir/src/main.cpp.o
robot_ui: CMakeFiles/robot_ui.dir/src/ros_page.cpp.o
robot_ui: CMakeFiles/robot_ui.dir/src/tm_ros_driver_windows.cpp.o
robot_ui: CMakeFiles/robot_ui.dir/build.make
robot_ui: /opt/ros/humble/lib/librclcpp_action.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_typesupport_fastrtps_c.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_typesupport_introspection_c.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_typesupport_introspection_cpp.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_typesupport_cpp.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_generator_py.so
robot_ui: /usr/lib/x86_64-linux-gnu/libQt5Quick.so.5.15.3
robot_ui: /usr/lib/x86_64-linux-gnu/libQt5Widgets.so.5.15.3
robot_ui: /opt/ros/humble/lib/librclcpp.so
robot_ui: /opt/ros/humble/lib/liblibstatistics_collector.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_generator_py.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/librosgraph_msgs__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_generator_py.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/libstatistics_msgs__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/librcl_action.so
robot_ui: /opt/ros/humble/lib/librcl.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_generator_py.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/librcl_interfaces__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/librcl_yaml_param_parser.so
robot_ui: /opt/ros/humble/lib/libyaml.so
robot_ui: /opt/ros/humble/lib/libtracetools.so
robot_ui: /opt/ros/humble/lib/librmw_implementation.so
robot_ui: /opt/ros/humble/lib/libament_index_cpp.so
robot_ui: /opt/ros/humble/lib/librcl_logging_spdlog.so
robot_ui: /opt/ros/humble/lib/librcl_logging_interface.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_generator_py.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/libaction_msgs__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_generator_py.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/libunique_identifier_msgs__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/librosidl_typesupport_fastrtps_c.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/librosidl_typesupport_fastrtps_cpp.so
robot_ui: /opt/ros/humble/lib/libfastcdr.so.1.0.24
robot_ui: /opt/ros/humble/lib/librmw.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/librosidl_typesupport_introspection_cpp.so
robot_ui: /opt/ros/humble/lib/librosidl_typesupport_introspection_c.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/librosidl_typesupport_cpp.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_generator_py.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_typesupport_c.so
robot_ui: /home/rslomron/tm_custom/install/tm_msgs/lib/libtm_msgs__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/libstd_msgs__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_generator_py.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/libbuiltin_interfaces__rosidl_generator_c.so
robot_ui: /opt/ros/humble/lib/librosidl_typesupport_c.so
robot_ui: /opt/ros/humble/lib/librcpputils.so
robot_ui: /opt/ros/humble/lib/librosidl_runtime_c.so
robot_ui: /opt/ros/humble/lib/librcutils.so
robot_ui: /usr/lib/x86_64-linux-gnu/libpython3.10.so
robot_ui: /usr/lib/x86_64-linux-gnu/libQt5QmlModels.so.5.15.3
robot_ui: /usr/lib/x86_64-linux-gnu/libQt5Qml.so.5.15.3
robot_ui: /usr/lib/x86_64-linux-gnu/libQt5Network.so.5.15.3
robot_ui: /usr/lib/x86_64-linux-gnu/libQt5Gui.so.5.15.3
robot_ui: /usr/lib/x86_64-linux-gnu/libQt5Core.so.5.15.3
robot_ui: CMakeFiles/robot_ui.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/rslomron/tm_custom/build/ui_for_debug_and_demo/CMakeFiles --progress-num=$(CMAKE_PROGRESS_6) "Linking CXX executable robot_ui"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/robot_ui.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/robot_ui.dir/build: robot_ui
.PHONY : CMakeFiles/robot_ui.dir/build

CMakeFiles/robot_ui.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/robot_ui.dir/cmake_clean.cmake
.PHONY : CMakeFiles/robot_ui.dir/clean

CMakeFiles/robot_ui.dir/depend: ui_tm_ros_driver_windows.h
	cd /home/rslomron/tm_custom/build/ui_for_debug_and_demo && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/rslomron/tm_custom/src/ui_for_debug_and_demo /home/rslomron/tm_custom/src/ui_for_debug_and_demo /home/rslomron/tm_custom/build/ui_for_debug_and_demo /home/rslomron/tm_custom/build/ui_for_debug_and_demo /home/rslomron/tm_custom/build/ui_for_debug_and_demo/CMakeFiles/robot_ui.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/robot_ui.dir/depend

