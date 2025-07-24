from datetime import timedelta

def calculate_yard_fee(entry_time, exit_time, daily_fee):
    duration = exit_time - entry_time
    total_days = int(duration.total_seconds() / 86400)
    if duration.total_seconds() % 86400 > 0:
        total_days += 1
    return total_days * daily_fee
