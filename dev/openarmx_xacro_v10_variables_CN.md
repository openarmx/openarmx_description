# OpenARM Xacro 与 v10 配置变量说明

本文档说明 `openarmx_arm.xacro` 中出现的“变量”（Xacro 宏参数/属性）来自哪里、分别代表什么含义，以及它们与 `config/arm/v10` 下 YAML 配置之间的关系与数据流。

## 总览：数据流与调用关系

- 入口模型：`urdf/robot/v10.urdf.xacro` 使用 `xacro.load_yaml(...)` 读取 v10 的 YAML 配置（关节限位、运动学、惯性等），并把这些字典作为参数传入上层宏 `openarmx_robot`。
- 机器人宏：`urdf/robot/openarmx_robot.xacro` 再调用手臂宏 `openarmx_arm`（以及机身/末端执行器宏），把对应的配置传进去。
- 手臂宏：`urdf/arm/openarmx_arm.xacro` 内部通过辅助宏（`openarmx-kinematics`、`openarmx-kinematics-link`、`openarmx-inertials`、`openarmx-limits`）将 YAML 中的数值写入 URDF 的 `<origin>`、`<inertial>`、`<limit>` 等元素。

简化示意：

```
[v10.urdf.xacro]
  ├─ load_yaml(joint_limits.yaml/inertials.yaml/kinematics.yaml/kinematics_link.yaml/kinematics_offset.yaml)
  └─ openarmx_robot(..., joint_limits=..., inertials=..., kinematics=..., kinematics_link=..., kinematics_offset=...)
       └─ openarmx_arm(... 同名参数 ...)
            ├─ openarmx-kinematics(来自 kinematics["jointN"].kinematic [+ offset])
            ├─ openarmx-kinematics-link(来自 kinematics_link["linkN"].kinematic)
            ├─ openarmx-inertials(来自 inertials["linkN"]) 
            └─ openarmx-limits(来自 joint_limits["jointN"].limit)
```

## 关键文件索引（v10）

- `urdf/robot/v10.urdf.xacro`：型号入口，加载 YAML 并传参给 `openarmx_robot`。
- `urdf/robot/openarmx_robot.xacro`：顶层机器人宏，调用手臂/机身/末端执行器宏。
- `urdf/arm/openarmx_arm.xacro`：手臂宏（定义 link0~link7、joint1~joint7）。
- `urdf/arm/openarmx_macro.xacro`：提供通用宏（惯量、限位、运动学、可视/碰撞对齐等）。
- `config/arm/v10/*.yaml`：手臂 v10 的参数库：
  - `joint_limits.yaml`、`kinematics.yaml`、`kinematics_link.yaml`、`kinematics_offset.yaml`、`inertials.yaml`。

## openarmx_arm.xacro 宏参数与意义

`openarmx_arm` 的主要参数（由上层传入）：

- `arm_type`：手臂型号（如 `v10`），用于网格路径等。
- `arm_prefix`：手臂前缀（如 `left_`/`right_`/空），用于命名链接与关节（最终前缀为 `openarmx_<arm_prefix>`，可由 `no_prefix` 关闭）。
- `no_prefix`：为 `true` 时不加 `openarmx_` 前缀。
- `description_pkg`：网格文件所在包（默认 `openarmx_description`）。
- `connected_to`、`xyz`、`rpy`：将整条手臂以固定关节连接到父链接（例如机身），设置装配位姿。
- `joint_limits`：来自 `joint_limits.yaml` 的字典；用于 `<limit>`（角度上下界、速度、力矩）。
- `inertials`：来自 `inertials.yaml` 的字典；用于 `<inertial>`（质心、质量、惯性张量）。
- `kinematics`：来自 `kinematics.yaml` 的字典；用于 `<joint>/<origin>`（父子之间的名义几何）。
- `kinematics_link`：来自 `kinematics_link.yaml` 的字典；用于 `<visual>/<collision>/<origin>`（网格对齐）。
- `kinematics_offset`：来自 `kinematics_offset.yaml` 的字典；可选附加偏置，叠加在 `kinematics` 上（常用于双臂装配或校准）。

额外内部变量：

- `reflect`：根据 `arm_prefix` 自动设置镜像系数（右臂 `+1`，左臂 `-1`），用于对称 Y 轴缩放/某些姿态与轴向；保证左右臂几何/惯性/轴向成镜像。
- `limit_offset_joint2`：双臂时对 `joint2` 限位的偏置（右臂 `+π/2`，左臂 `-π/2`），使双臂装配角度合理。

## config/arm/v10 下 YAML 的字段与用途

- `joint_limits.yaml`（关节限制与能力）
  - `jointN.limit.lower/upper`：角度上下界（弧度）。
  - `jointN.limit.velocity`：最大角速度（rad/s）。
  - `jointN.limit.effort`：最大力矩/力（Nm）。
  - 在 Xacro 中经 `openarmx-limits` 宏写入 `<limit>`，并考虑 `reflect` 和（可选）`offset`（如 joint2 的左右偏置）。

- `kinematics.yaml`（关节名义几何）
  - `jointN.kinematic.x/y/z/roll/pitch/yaw`：父 link 到该关节原点的位姿（米/弧度）。
  - 在 Xacro 中经 `openarmx-kinematics` 宏写入各 `<joint>/<origin>`；若提供 `kinematics_offset`，则将 `offset` 与 `kinematics` 相加后生效。

- `kinematics_link.yaml`（link 网格对齐）
  - `linkN.kinematic.x/y/z/roll/pitch/yaw`：仅用于 `<visual>/<collision>` 的 `<origin>`，确保 CAD 网格与 link 坐标系对齐；不改变关节拓扑。
  - 在 Xacro 中经 `openarmx-kinematics-link` 宏应用到每个 link 的可视和碰撞几何。

- `kinematics_offset.yaml`（名义几何附加修正）
  - `jointN.kinematic_offset.x/y/z/roll/pitch/yaw`：在需要时叠加到 `kinematics` 上（例如 v10 双臂中 `joint2.roll ≈ π/2`）。

- `inertials.yaml`（每个 link 的惯性属性）
  - `linkN.origin.x/y/z/roll/pitch/yaw`：质心相对 link 原点的位姿。
  - `linkN.mass`：质量（kg）。
  - `linkN.inertia.xx/xy/xz/yy/yz/zz`：惯性张量元素。
  - 在 Xacro 中经 `openarmx-inertials` 宏写入 `<inertial>`，并对 Y 方向根据 `reflect` 做镜像处理。

## 左右臂镜像与双臂差异

- 镜像（`reflect`）：右臂为 `+1`，左臂为 `-1`。影响：
  - 可视/碰撞网格缩放的 Y 轴符号（网格镜像）。
  - 惯性中质心 `origin.y` 的符号。
  - 某些关节轴方向与末端关节的绕轴方向（例如 joint7 的 `axis xyz="0 ±1 0"`）。
- 双臂偏置：
  - `joint2` 应用 `limit_offset_joint2`（±π/2）以区分左右臂的装配位姿范围。
  - 在双臂模式下通常还会传入 `kinematics_offset`，进一步对某些关节位姿做固定偏转（如 `joint2.roll`）。

## 修改与验证建议

- 修改位置：优先在源码包下编辑（而非 `install/` 目录）：
  - YAML：`src/openarmx_description/config/arm/v10/*.yaml`
  - Xacro：`src/openarmx_description/urdf/**/*.xacro`
- 构建与查看：
  - 构建：`colcon build --symlink-install`
  - 环境：`source install/setup.bash`
  - RViz 展示：`ros2 launch openarmx_description display_openarmx.launch.py arm_type:=v10 ee_type:=openarmx_hand bimanual:=false`
- 小贴士：
  - 仅调整网格对齐请改 `kinematics_link.yaml`；
  - 调整关节零位/连杆长度请改 `kinematics.yaml`（必要时配合 `kinematics_offset.yaml` 做小幅校准）；
  - 调整负载与动力学请改 `inertials.yaml`；
  - 限位/速度/力矩能力请改 `joint_limits.yaml`。

## 参考（关键实现位置）

- 入口与加载：`urdf/robot/v10.urdf.xacro`
- 机器人宏：`urdf/robot/openarmx_robot.xacro`
- 手臂宏：`urdf/arm/openarmx_arm.xacro`
- 通用宏：`urdf/arm/openarmx_macro.xacro`
- 参数库：`config/arm/v10/*.yaml`


## 代码位置与行号（便于快速定位）

- `urdf/arm/openarmx_arm.xacro`
  - `urdf/arm/openarmx_arm.xacro:6` 定义 `openarmx_arm` 宏参数列表。
  - `urdf/arm/openarmx_arm.xacro:8` 计算命名前缀 `prefix`（结合 `arm_prefix` 与 `no_prefix`）。
  - `urdf/arm/openarmx_arm.xacro:10` 右臂 `reflect=+1`；`urdf/arm/openarmx_arm.xacro:14` 左臂 `reflect=-1`。
  - `urdf/arm/openarmx_arm.xacro:18` 若挂接到父链接则创建固定关节；`urdf/arm/openarmx_arm.xacro:22` 设置该固定关节的装配位姿 `xyz/rpy`。
  - `urdf/arm/openarmx_arm.xacro:26` link0 可视/碰撞/惯量生成；`urdf/arm/openarmx_arm.xacro:28` link1 同理。
  - `urdf/arm/openarmx_arm.xacro:31` `joint1` 用 `kinematics` 写 `<origin>`；`urdf/arm/openarmx_arm.xacro:35` `joint1` 限位（支持偏置）。
  - `urdf/arm/openarmx_arm.xacro:41` `limit_offset_joint2` 默认 0；`urdf/arm/openarmx_arm.xacro:44` 右臂设为 `+pi/2`；`urdf/arm/openarmx_arm.xacro:48` 左臂设为 `-pi/2`。
  - `urdf/arm/openarmx_arm.xacro:52` `joint2` 引用 `kinematics_offset` 与 `reflect`；`urdf/arm/openarmx_arm.xacro:56` `joint2` 限位叠加左右偏置。
  - `urdf/arm/openarmx_arm.xacro:62`/`72`/`82`/`92`/`102` 各关节用 `kinematics` 写 `<origin>`（示例：`joint3` 在 `:62`）。
  - `urdf/arm/openarmx_arm.xacro:105` `joint7` 轴向使用 `reflect`（`axis xyz="0 ±1 0"`）。

- `urdf/arm/openarmx_macro.xacro`
  - `urdf/arm/openarmx_macro.xacro:4` 宏 `openarmx-inertials` 定义；`urdf/arm/openarmx_macro.xacro:12` `<inertial>/<origin>` 中 `y` 乘以 `reflect`；`urdf/arm/openarmx_macro.xacro:17` `<inertia>` 元素。
  - `urdf/arm/openarmx_macro.xacro:24` 宏 `link_with_sc`；`urdf/arm/openarmx_macro.xacro:31` 可视网格路径与缩放（含 `reflect`）；`urdf/arm/openarmx_macro.xacro:37` 碰撞网格路径；`urdf/arm/openarmx_macro.xacro:41` 调用 `openarmx-inertials`。
  - `urdf/arm/openarmx_macro.xacro:91` 宏 `openarmx-limits`；`urdf/arm/openarmx_macro.xacro:92` 读取 `limits`；`urdf/arm/openarmx_macro.xacro:109` 输出 `<limit>`。
  - `urdf/arm/openarmx_macro.xacro:116` 宏 `openarmx-kinematics`；`urdf/arm/openarmx_macro.xacro:121` 含 offset 的 `<origin>`；`urdf/arm/openarmx_macro.xacro:127` 无 offset 的 `<origin>`。
  - `urdf/arm/openarmx_macro.xacro:131` 宏 `openarmx-kinematics-link`；`urdf/arm/openarmx_macro.xacro:133` link 的 `<origin>`。

- `urdf/robot/v10.urdf.xacro`
  - `urdf/robot/v10.urdf.xacro:36` 加载 `joint_limits.yaml`；`urdf/robot/v10.urdf.xacro:37` 加载 `inertials.yaml`；`urdf/robot/v10.urdf.xacro:38` 加载 `kinematics.yaml`；`urdf/robot/v10.urdf.xacro:39` 加载 `kinematics_link.yaml`；`urdf/robot/v10.urdf.xacro:40` 加载 `kinematics_offset.yaml`。

- `urdf/robot/openarmx_robot.xacro`
  - `urdf/robot/openarmx_robot.xacro:73` 左臂调用 `openarmx_arm`；`urdf/robot/openarmx_robot.xacro:85` 明确传入 `kinematics_offset`。
  - `urdf/robot/openarmx_robot.xacro:88` 右臂调用 `openarmx_arm`；`urdf/robot/openarmx_robot.xacro:100` 明确传入 `kinematics_offset`。
  - `urdf/robot/openarmx_robot.xacro:149` 单臂调用 `openarmx_arm`；`urdf/robot/openarmx_robot.xacro:156`/`157`/`158` 分别传入 `kinematics`/`kinematics_link`/`inertials`（未传 `kinematics_offset`）。

## 关节轴向总览（来自 openarmx_arm.xacro）

```
joint1: axis = 0 0 1
joint2: axis = -1 0 0
joint3: axis = 0 0 1
joint4: axis = 0 1 0
joint5: axis = 0 0 1
joint6: axis = 1 0 0
joint7: axis = 0 (reflect) 0   # reflect: 右臂 +1, 左臂 -1
```

