import subprocess

print("Starting service")

cmd = "systemctl --user start zouip_sender.service"
    
subprocess.call(cmd, shell = True)
