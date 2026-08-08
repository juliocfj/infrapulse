from infrapulse.checks.cpu import check_cpu
from infrapulse.checks.memory import check_memory


print("InfraPulse - Infrastructure Health Monitor")

cpu_result = check_cpu()
memory_result = check_memory()

print(cpu_result)
print(memory_result)
