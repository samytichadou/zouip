import os, subprocess, sys, time, threading

cmd = "netcat -l -v -k 12345"


result = subprocess.run(
    ["netcat", "-l", "-v", "12345"], capture_output=True, text=True
)
print("stdout:", result.stdout)
print("stderr:", result.stderr)

# subprocess.call(cmd, shell=True)

# p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
#  
# ## But do not wait till netstat finish, start displaying output immediately ##
# while True:
#     out = str(p.stderr.read(1))
#     if out == '' and p.poll() != None:
#         break
#     if out != '':
#         sys.stdout.write(out)
#         sys.stdout.flush()

def to_thread_func():
    proc = subprocess.Popen(["netcat", "-l", "-k", "12345"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("start")

    # while proc.poll() is None:
    #     print("running")
    #     output = proc.communicate()[0].decode("utf-8")
    #     print(output)
    #     time.sleep(1)
        
    while True:
    # while proc.poll() is None:
        #print("start reading")
        line = proc.stdout.readline()
        if str(line) != "b''" :
            print(line)
            print("new")
        #     if b"Append frame " in line :
        #         frame_count += 1
        #         try :
        #             scene.playblaster_completion = frame_count / total_frame * 100
        #         except AttributeError :
        #             #debug
        #             #print("AttributeError avoided")
        #             pass
        # 
        #     if b"Blender quit" in line :
        #         break
        # else:
        #     break

    # print(output)
    print("end")
# arguments = []
# render_thread = threading.Thread(target=to_thread_func, args=arguments)
# render_thread.start()
