def calculate_overall_status(results):
    statuses = [result["status"] for result in results if "status" in result]

    if "critical" in statuses:
        return "critical"

    if "warning" in statuses:
        return "warning"

    return "healthy"
