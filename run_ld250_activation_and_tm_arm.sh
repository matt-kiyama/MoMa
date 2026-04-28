#!/usr/bin/env bash
set -euo pipefail

# Defaults can be overridden at runtime:
#   ROS_STATIC_PEERS='1.2.3.4' TMR_WS="$HOME/tmr_ros2-humble" TM_ROBOT_IP='169.254.92.124' ./run_ld250_activation_and_tm_arm.sh
ROS_STATIC_PEERS="${ROS_STATIC_PEERS:-1.2.3.4}"
TMR_WS="${TMR_WS:-$HOME/tmr_ros2-humble}"
TM_ROBOT_IP="${TM_ROBOT_IP:-169.254.92.124}"

run_cmd() {
  printf '\n$ %s\n' "$*"
  "$@"
}

source_allow_unset() {
  local had_u=0
  if [[ $- == *u* ]]; then
    had_u=1
    set +u
  fi
  # shellcheck disable=SC1090
  source "$1"
  if (( had_u )); then
    set -u
  fi
}

if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  printf 'Missing ROS setup: /opt/ros/jazzy/setup.bash\n' >&2
  exit 1
fi

# ----------------------
# Activation part (Workflow as of 10/23/25)
# ----------------------
source_allow_unset /opt/ros/jazzy/setup.bash
export ROS_STATIC_PEERS

run_cmd ros2 lifecycle get /platform/manager
run_cmd ros2 lifecycle set /platform/manager configure
run_cmd ros2 lifecycle set /platform/manager activate

# ----------------------
# Workflow for getting the TM Arm running
# (echo commands intentionally excluded)
# ----------------------
if [[ ! -d "$TMR_WS" ]]; then
  printf 'TM workspace not found: %s\n' "$TMR_WS" >&2
  exit 1
fi

if [[ -f /opt/ros/humble/setup.bash ]]; then
  source_allow_unset /opt/ros/humble/setup.bash
else
  # Fall back to current ROS env if humble isn't present.
  source_allow_unset /opt/ros/jazzy/setup.bash
fi

cd "$TMR_WS"
run_cmd colcon build

if [[ ! -f "$TMR_WS/install/setup.bash" ]]; then
  printf 'Build finished, but missing setup file: %s/install/setup.bash\n' "$TMR_WS" >&2
  exit 1
fi

source_allow_unset "$TMR_WS/install/setup.bash"

# Runs in foreground (Ctrl+C to stop)
run_cmd ros2 run tm_driver tm_driver "robot_ip:=${TM_ROBOT_IP}"
