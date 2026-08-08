from infrapulse.checks.cpu import check_cpu


print("InfraPulse - Infrastructure Health Monitor")

cpu_result = check_cpu()
print(cpu_result)
