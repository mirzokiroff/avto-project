from datetime import timedelta

def calculate_fee(entry_time, exit_time):
    total_days = (exit_time - entry_time).days + 1
    daily_rate = 50000  # So‘m
    return total_days * daily_rate
