from infrapulse.checks.cpu import check_cpu
from infrapulse.checks.disk import check_disk
from infrapulse.checks.memory import check_memory
from infrapulse.checks.uptime import check_uptime


def bytes_to_gb(value):
    return value / (1024**3)


print("InfraPulse - Infrastructure Health Monitor")
print()

cpu_result = check_cpu()
disk_result = check_disk()
memory_result = check_memory()
uptime_result = check_uptime()

print("CPU")
print(f"Usage: {cpu_result['value']}{cpu_result['unit']}")
print(f"Status: {cpu_result['status'].upper()}")
print()

print("Memory")
print(f"Usage: {memory_result['value']}{memory_result['unit']}")
print(f"Status: {memory_result['status'].upper()}")
print()

print("Disk")
print(f"Usage: {disk_result['value']}{disk_result['unit']}")
print(f"Total: {bytes_to_gb(disk_result['total_bytes']):.1f} GB")
print(f"Used: {bytes_to_gb(disk_result['used_bytes']):.1f} GB")
print(f"Free: {bytes_to_gb(disk_result['free_bytes']):.1f} GB")
print(f"Status: {disk_result['status'].upper()}")
print()

print("Uptime")
print(
    f"{uptime_result['days']} days, "
    f"{uptime_result['hours']} hours, "
    f"{uptime_result['minutes']} minutes"
)
