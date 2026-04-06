# Z push cycles, then return home 

# Uses Ethernet IP directly 

 

import os  

import sys 

import time 

 

sys.path.append(os.path.join(os.path.dirname(file), '../../..')) 

from xarm.wrapper import XArmAPI 

 

# Hardcode robot IP 

ip = "192.168.0.220" 

arm = XArmAPI(ip, do_not_open=True) 

arm.connect() 

 

# Basic init 

arm.clean_error() 

arm.clean_warn() 

arm.motion_enable(True) 

arm.set_mode(0)# position control 

arm.set_state(0) # ready 

time.sleep(1) 

 

print("Going home...") 

arm.move_gohome(wait=True) 

time.sleep(1) 

Read start pose 

code, pose = arm.get_position(is_radian=False) 

if code != 0: 

print("Failed to get position, code=", code) 

arm.disconnect() 

sys.exit(1) 

x, y, z, roll, pitch, yaw = pose 

original_z = z 

print("Start pose:", pose) 

---------------- SETTINGS ---------------- 

speed = 30 # keep low for safety (20–80) 

push_down_mm = -130 

cycles = 5 

total_time_sec = 30 

Safety: never push more than this above starting Z 

max_push_mm = 5 

max_z = original_z + max_push_mm 

------------------------------------------ 

 

cycle_time = total_time_sec / cycles 

print(f"Running {cycles} cycles over {total_time_sec}s | original_z={original_z:.2f} | max_z={max_z:.2f}") 

 

def ensure_ready(): 

# state=4 means stopped; error_code != 0 means fault/alarm 

if arm.state == 4 or arm.error_code != 0: 

print(f"[RECOVER] state={arm.state}, err={arm.error_code},		warn={arm.warn_code}") 

arm.clean_error() 

arm.clean_warn() 

arm.motion_enable(True) 

arm.set_mode(0) 

arm.set_state(0) 

time.sleep(0.5) 

for i in range(cycles): 

print(f"\nCycle {i+1}/{cycles}")  

ensure_ready() 

 
target_z = original_z + push_down_mm 
 
# Clamp to safe max 
if target_z > max_z: 
    target_z = max_z 
    print(f"[CLAMP] target_z clamped to {target_z:.2f}") 
 
# Push down 
code = arm.set_position( 
    x=x, y=y, z=target_z, 
    roll=roll, pitch=pitch, yaw=yaw, 
    speed=speed, 
    wait=True 
) 
if code != 0: 
    print(f"[ERROR] push down failed code={code}") 
    ensure_ready() 
    continue 
 
# Return up to original 
code = arm.set_position( 
    x=x, y=y, z=original_z, 
    roll=roll, pitch=pitch, yaw=yaw, 
    speed=speed, 
    wait=True 
) 
if code != 0: 
    print(f"[ERROR] return up failed code={code}") 
    ensure_ready() 
    continue 
 
# Keep total duration ~30s 
time.sleep(max(0, cycle_time - 2)) 
  

print("\nReturning home...") 

ensure_ready() 

arm.move_gohome(wait=True) 

print("Done.") 

arm.disconnect() 
