import os
import time
import signal
import bota_driver
import sys

import pandas as pd  # 新增：写Excel

stop_flag = False

def signal_handler(signum, frame):
    global stop_flag
    stop_flag = True

signal.signal(signal.SIGINT, signal_handler)

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ 串口模式：确保你用的是 bota_binary.json
config_path = os.path.join(project_root, "bota_driver_config", "Bota_Binary.json")

# ===== 新增：用于存储数据的变量 =====
records = []  # 每个元素是一行数据(dict)

try:
    bota_ft_sensor_driver = bota_driver.BotaDriver(config_path)
    print(f" >>>>>>>>>>> BotaDriver version: {bota_ft_sensor_driver.get_driver_version_string()} <<<<<<<<<<<< ")

    if not bota_ft_sensor_driver.configure():
        raise RuntimeError("Failed to configure driver")

    if not bota_ft_sensor_driver.tare():
        raise RuntimeError("Failed to tare sensor")

    if not bota_ft_sensor_driver.activate():
        raise RuntimeError("Failed to activate driver")

    EXAMPLE_DURATION = 100.0      #seconds
    READING_FREQUENCY = 100.0   # 建议：和传感器 100Hz 对齐（日志里写 expected 100Hz）
    PRINTING_FREQUENCY = 1.0


    start_time = time.perf_counter()
    last_print_time = start_time
    next_execution_time = start_time

    while time.perf_counter() - start_time < EXAMPLE_DURATION and not stop_flag:
        # 读一帧（建议加个简单防护，避免偶发异常直接崩）
        try:
            bota_frame = bota_ft_sensor_driver.read_frame()
        except Exception as e:
            print(f"[WARN] read_frame failed: {e}")
            continue

        status = bota_frame.status
        force = bota_frame.force
        torque = bota_frame.torque
        timestamp = bota_frame.timestamp
        temperature = bota_frame.temperature
        acceleration = bota_frame.acceleration
        angular_rate = bota_frame.angular_rate

        # ===== 新增：把这一帧写入 records =====
        records.append({
            # 时间（两种都存：PC本地时间 + 传感器时间戳）
            "pc_time_s": time.time(),                # Unix 时间（秒）
            "sensor_timestamp": timestamp,           # 传感器时间戳（单位看驱动定义）

            # 状态位（拆开存，Excel里更好筛选）
            "throttled": int(status.throttled),
            "overrange": int(status.overrange),
            "invalid": int(status.invalid),
            "raw": int(status.raw),

            # 力（N）
            "Fx_N": float(force[0]),
            "Fy_N": float(force[1]),
            "Fz_N": float(force[2]),

            # 力矩（Nm）
            "Tx_Nm": float(torque[0]),
            "Ty_Nm": float(torque[1]),
            "Tz_Nm": float(torque[2]),

            # IMU（如果你的配置里没开，这里会是0）
            "Ax_mps2": float(acceleration[0]),
            "Ay_mps2": float(acceleration[1]),
            "Az_mps2": float(acceleration[2]),
            "Gx_rps": float(angular_rate[0]),
            "Gy_rps": float(angular_rate[1]),
            "Gz_rps": float(angular_rate[2]),

            # 温度（你的日志里是 0.0，照样存）
            "Temp_C": float(temperature),
        })

        # 按打印频率输出
        current_time = time.perf_counter()
        if current_time - last_print_time >= 1.0 / PRINTING_FREQUENCY:
            print("----------------------------")
            print(f"Status: [throttled={status.throttled}, overrange={status.overrange}, invalid={status.invalid}, raw={status.raw}]")
            print(f"Force: [{force[0]}, {force[1]}, {force[2]}] N")
            print(f"Torque: [{torque[0]}, {torque[1]}, {torque[2]}] Nm")
            print(f"Temperature: {temperature} °C")
            print(f"Timestamp: {timestamp}")
            print("----------------------------")
            last_print_time = current_time

        # 节拍控制
        next_execution_time += 1.0 / READING_FREQUENCY
        sleep_time = max(0, next_execution_time - time.perf_counter())
        time.sleep(sleep_time)

    # 退出前关闭驱动
    bota_ft_sensor_driver.deactivate()
    bota_ft_sensor_driver.shutdown()

    print("Completion WITHOUT errors.")

except Exception as e:
    print(f"FATAL: {e}")
    print("Completion WITH errors.")

finally:
    # ===== 新增：无论是否异常，都尽量把已经采集到的数据写出去 =====
    try:
        if len(records) > 0:
            df = pd.DataFrame(records)

            # 输出路径：放在当前脚本目录下
            out_dir = os.path.dirname(os.path.abspath(__file__))
            out_path = os.path.join(out_dir, f"bota_log_{time.strftime('%Y%m%d_%H%M%S')}.xlsx")

            # 写Excel
            df.to_excel(out_path, index=False, sheet_name="bota_data")

            print(f"[OK] Saved {len(df)} rows to Excel: {out_path}")
        else:
            print("[WARN] No data collected, Excel not created.")
    except Exception as e:
        print(f"[WARN] Failed to write Excel: {e}")

    print("EXITING PROGRAM")
    sys.exit(0)