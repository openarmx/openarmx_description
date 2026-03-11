# OpenARM Xacro and v10 Configuration Variables Guide

This document explains the "variables" (Xacro macro parameters/properties) used in `openarmx_arm.xacro`, their origins, meanings, and the relationship and data flow between them and the YAML configurations under `config/arm/v10`.

## Overview: Data Flow and Call Hierarchy

- Entry model: `urdf/robot/v10.urdf.xacro` uses `xacro.load_yaml(...)` to load v10 YAML configurations (joint limits, kinematics, inertials, etc.) and passes these dictionaries as parameters to the top-level macro `openarmx_robot`.
- Robot macro: `urdf/robot/openarmx_robot.xacro` calls the arm macro `openarmx_arm` (along with body/end-effector macros), passing the corresponding configurations.
- Arm macro: `urdf/arm/openarmx_arm.xacro` internally uses helper macros (`openarmx-kinematics`, `openarmx-kinematics-link`, `openarmx-inertials`, `openarmx-limits`) to write values from YAML into URDF elements like `<origin>`, `<inertial>`, `<limit>`, etc.

Simplified diagram:

```
[v10.urdf.xacro]
  ├─ load_yaml(joint_limits.yaml/inertials.yaml/kinematics.yaml/kinematics_link.yaml/kinematics_offset.yaml)
  └─ openarmx_robot(..., joint_limits=..., inertials=..., kinematics=..., kinematics_link=..., kinematics_offset=...)
       └─ openarmx_arm(... same parameters ...)
            ├─ openarmx-kinematics(from kinematics["jointN"].kinematic [+ offset])
            ├─ openarmx-kinematics-link(from kinematics_link["linkN"].kinematic)
            ├─ openarmx-inertials(from inertials["linkN"])
            └─ openarmx-limits(from joint_limits["jointN"].limit)
```

## Key File Index (v10)

- `urdf/robot/v10.urdf.xacro`: Model entry point, loads YAML and passes parameters to `openarmx_robot`.
- `urdf/robot/openarmx_robot.xacro`: Top-level robot macro, calls arm/body/end-effector macros.
- `urdf/arm/openarmx_arm.xacro`: Arm macro (defines link0~link7, joint1~joint7).
- `urdf/arm/openarmx_macro.xacro`: Provides utility macros (inertia, limits, kinematics, visual/collision alignment, etc.).
- `config/arm/v10/*.yaml`: v10 arm parameter library:
  - `joint_limits.yaml`, `kinematics.yaml`, `kinematics_link.yaml`, `kinematics_offset.yaml`, `inertials.yaml`.

## openarmx_arm.xacro Macro Parameters and Meanings

Main parameters of `openarmx_arm` (passed from parent):

- `arm_type`: Arm model (e.g., `v10`), used for mesh paths, etc.
- `arm_prefix`: Arm prefix (e.g., `left_`/`right_`/empty), used for naming links and joints (final prefix is `openarmx_<arm_prefix>`, can be disabled by `no_prefix`).
- `no_prefix`: When `true`, disables the `openarmx_` prefix.
- `description_pkg`: Package containing mesh files (default: `openarmx_description`).
- `connected_to`, `xyz`, `rpy`: Connects the entire arm to a parent link (e.g., body) via a fixed joint, setting the mounting pose.
- `joint_limits`: Dictionary from `joint_limits.yaml`; used for `<limit>` (angle bounds, velocity, torque).
- `inertials`: Dictionary from `inertials.yaml`; used for `<inertial>` (center of mass, mass, inertia tensor).
- `kinematics`: Dictionary from `kinematics.yaml`; used for `<joint>/<origin>` (nominal geometry between parent and child).
- `kinematics_link`: Dictionary from `kinematics_link.yaml`; used for `<visual>/<collision>/<origin>` (mesh alignment).
- `kinematics_offset`: Dictionary from `kinematics_offset.yaml`; optional additional offset, added to `kinematics` (commonly used for bimanual mounting or calibration).

Additional internal variables:

- `reflect`: Automatically set based on `arm_prefix` as a mirroring coefficient (right arm `+1`, left arm `-1`), used for symmetric Y-axis scaling/certain poses and axes; ensures left/right arm geometry/inertia/axes are mirrored.
- `limit_offset_joint2`: Offset for `joint2` limits in bimanual mode (right arm `+π/2`, left arm `-π/2`), making bimanual mounting angles reasonable.

## YAML Fields and Usage under config/arm/v10

- `joint_limits.yaml` (Joint constraints and capabilities)
  - `jointN.limit.lower/upper`: Angle bounds (radians).
  - `jointN.limit.velocity`: Maximum angular velocity (rad/s).
  - `jointN.limit.effort`: Maximum torque/force (Nm).
  - Written to `<limit>` via `openarmx-limits` macro in Xacro, considering `reflect` and (optional) `offset` (e.g., left/right offset for joint2).

- `kinematics.yaml` (Joint nominal geometry)
  - `jointN.kinematic.x/y/z/roll/pitch/yaw`: Pose from parent link to joint origin (meters/radians).
  - Written to each `<joint>/<origin>` via `openarmx-kinematics` macro in Xacro; if `kinematics_offset` is provided, `offset` is added to `kinematics` before taking effect.

- `kinematics_link.yaml` (Link mesh alignment)
  - `linkN.kinematic.x/y/z/roll/pitch/yaw`: Only used for `<visual>/<collision>` `<origin>`, ensuring CAD meshes align with link coordinate frames; does not change joint topology.
  - Applied to visual and collision geometry of each link via `openarmx-kinematics-link` macro in Xacro.

- `kinematics_offset.yaml` (Nominal geometry additional correction)
  - `jointN.kinematic_offset.x/y/z/roll/pitch/yaw`: Added to `kinematics` when needed (e.g., in v10 bimanual, `joint2.roll ≈ π/2`).

- `inertials.yaml` (Inertial properties for each link)
  - `linkN.origin.x/y/z/roll/pitch/yaw`: Center of mass pose relative to link origin.
  - `linkN.mass`: Mass (kg).
  - `linkN.inertia.xx/xy/xz/yy/yz/zz`: Inertia tensor elements.
  - Written to `<inertial>` via `openarmx-inertials` macro in Xacro, with Y-direction mirroring based on `reflect`.

## Left/Right Arm Mirroring and Bimanual Differences

- Mirroring (`reflect`): Right arm is `+1`, left arm is `-1`. Affects:
  - Y-axis sign in visual/collision mesh scaling (mesh mirroring).
  - Sign of center of mass `origin.y` in inertials.
  - Some joint axis directions and end joint rotation directions (e.g., joint7's `axis xyz="0 ±1 0"`).
- Bimanual offset:
  - `joint2` applies `limit_offset_joint2` (±π/2) to differentiate left/right arm mounting pose ranges.
  - In bimanual mode, `kinematics_offset` is typically passed to further apply fixed rotations to certain joint poses (e.g., `joint2.roll`).

## Modification and Verification Recommendations

- Modification location: Prioritize editing in source package (not `install/` directory):
  - YAML: `src/openarmx_description/config/arm/v10/*.yaml`
  - Xacro: `src/openarmx_description/urdf/**/*.xacro`
- Build and view:
  - Build: `colcon build --symlink-install`
  - Environment: `source install/setup.bash`
  - RViz display: `ros2 launch openarmx_description display_openarmx.launch.py arm_type:=v10 ee_type:=openarmx_hand bimanual:=false`
- Tips:
  - For mesh alignment only, modify `kinematics_link.yaml`;
  - For joint zero position/link length, modify `kinematics.yaml` (use `kinematics_offset.yaml` for minor calibration if needed);
  - For payload and dynamics, modify `inertials.yaml`;
  - For limits/velocity/torque capabilities, modify `joint_limits.yaml`.

## Reference (Key Implementation Locations)

- Entry and loading: `urdf/robot/v10.urdf.xacro`
- Robot macro: `urdf/robot/openarmx_robot.xacro`
- Arm macro: `urdf/arm/openarmx_arm.xacro`
- Utility macros: `urdf/arm/openarmx_macro.xacro`
- Parameter library: `config/arm/v10/*.yaml`


## Code Locations and Line Numbers (for quick reference)

- `urdf/arm/openarmx_arm.xacro`
  - `urdf/arm/openarmx_arm.xacro:6` defines `openarmx_arm` macro parameter list.
  - `urdf/arm/openarmx_arm.xacro:8` calculates naming prefix `prefix` (combining `arm_prefix` and `no_prefix`).
  - `urdf/arm/openarmx_arm.xacro:10` right arm `reflect=+1`; `urdf/arm/openarmx_arm.xacro:14` left arm `reflect=-1`.
  - `urdf/arm/openarmx_arm.xacro:18` creates fixed joint if attached to parent link; `urdf/arm/openarmx_arm.xacro:22` sets mounting pose `xyz/rpy` for that fixed joint.
  - `urdf/arm/openarmx_arm.xacro:26` link0 visual/collision/inertia generation; `urdf/arm/openarmx_arm.xacro:28` link1 likewise.
  - `urdf/arm/openarmx_arm.xacro:31` `joint1` uses `kinematics` to write `<origin>`; `urdf/arm/openarmx_arm.xacro:35` `joint1` limits (supports offset).
  - `urdf/arm/openarmx_arm.xacro:41` `limit_offset_joint2` defaults to 0; `urdf/arm/openarmx_arm.xacro:44` right arm set to `+pi/2`; `urdf/arm/openarmx_arm.xacro:48` left arm set to `-pi/2`.
  - `urdf/arm/openarmx_arm.xacro:52` `joint2` references `kinematics_offset` and `reflect`; `urdf/arm/openarmx_arm.xacro:56` `joint2` limits add left/right offset.
  - `urdf/arm/openarmx_arm.xacro:62`/`72`/`82`/`92`/`102` each joint uses `kinematics` to write `<origin>` (example: `joint3` at `:62`).
  - `urdf/arm/openarmx_arm.xacro:105` `joint7` axis uses `reflect` (`axis xyz="0 ±1 0"`).

- `urdf/arm/openarmx_macro.xacro`
  - `urdf/arm/openarmx_macro.xacro:4` macro `openarmx-inertials` definition; `urdf/arm/openarmx_macro.xacro:12` `<inertial>/<origin>` `y` multiplied by `reflect`; `urdf/arm/openarmx_macro.xacro:17` `<inertia>` elements.
  - `urdf/arm/openarmx_macro.xacro:24` macro `link_with_sc`; `urdf/arm/openarmx_macro.xacro:31` visual mesh path and scaling (includes `reflect`); `urdf/arm/openarmx_macro.xacro:37` collision mesh path; `urdf/arm/openarmx_macro.xacro:41` calls `openarmx-inertials`.
  - `urdf/arm/openarmx_macro.xacro:91` macro `openarmx-limits`; `urdf/arm/openarmx_macro.xacro:92` reads `limits`; `urdf/arm/openarmx_macro.xacro:109` outputs `<limit>`.
  - `urdf/arm/openarmx_macro.xacro:116` macro `openarmx-kinematics`; `urdf/arm/openarmx_macro.xacro:121` `<origin>` with offset; `urdf/arm/openarmx_macro.xacro:127` `<origin>` without offset.
  - `urdf/arm/openarmx_macro.xacro:131` macro `openarmx-kinematics-link`; `urdf/arm/openarmx_macro.xacro:133` link's `<origin>`.

- `urdf/robot/v10.urdf.xacro`
  - `urdf/robot/v10.urdf.xacro:36` loads `joint_limits.yaml`; `urdf/robot/v10.urdf.xacro:37` loads `inertials.yaml`; `urdf/robot/v10.urdf.xacro:38` loads `kinematics.yaml`; `urdf/robot/v10.urdf.xacro:39` loads `kinematics_link.yaml`; `urdf/robot/v10.urdf.xacro:40` loads `kinematics_offset.yaml`.

- `urdf/robot/openarmx_robot.xacro`
  - `urdf/robot/openarmx_robot.xacro:73` left arm calls `openarmx_arm`; `urdf/robot/openarmx_robot.xacro:85` explicitly passes `kinematics_offset`.
  - `urdf/robot/openarmx_robot.xacro:88` right arm calls `openarmx_arm`; `urdf/robot/openarmx_robot.xacro:100` explicitly passes `kinematics_offset`.
  - `urdf/robot/openarmx_robot.xacro:149` single arm calls `openarmx_arm`; `urdf/robot/openarmx_robot.xacro:156`/`157`/`158` pass `kinematics`/`kinematics_link`/`inertials` respectively (no `kinematics_offset` passed).

## Joint Axis Overview (from openarmx_arm.xacro)

```
joint1: axis = 0 0 1
joint2: axis = -1 0 0
joint3: axis = 0 0 1
joint4: axis = 0 1 0
joint5: axis = 0 0 1
joint6: axis = 1 0 0
joint7: axis = 0 (reflect) 0   # reflect: right arm +1, left arm -1
```
