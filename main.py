from infrapulse.checks.cpu import check_cpu
from infrapulse.checks.disk import check_disk
from infrapulse.checks.memory import check_memory
from infrapulse.checks.uptime import check_uptime


print("InfraPulse - Infrastructure Health Monitor")

cpu_result = check_cpu()
disk_result = check_disk()
memory_result = check_memory()
uptime_result = check_uptime()

print(cpu_result)
print(disk_result)
print(memory_result)
print(uptime_result)
