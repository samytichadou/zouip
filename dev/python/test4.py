import subprocess, time

# Define the command to run as a list of arguments
command = ["netcat", "-l", "-v", "-k", "12340"]

# Start the subprocess in the background
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

print(process.pid)

# You can communicate with the subprocess if needed
# For example, sending data to stdin and reading from stdout/stderr
# time.sleep(3)
# print("input")
# time.sleep(3)
# print("flush")
# process.stdin.flush()

#process.kill()

start_time = time.perf_counter()
print(start_time)

while True:
    #print(time.perf_counter())
    end_time = time.perf_counter()
    if end_time-start_time > 20:
        print("stop")
        break
    # if process.poll():
    #     break
    line = process.stdout.readline()
    if line:
        print(line)
        # process.stdin.write(b"answer\n")

process.kill()

# output, error = process.communicate()

# Optionally, wait for the subprocess to finish
# process.wait()

# Print the output and error (if any)
# print("Output:", output.decode())
# print("Error:", error.decode())
