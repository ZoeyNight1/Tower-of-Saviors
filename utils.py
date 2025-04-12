import datetime

def calculate_full_time(max_stamina, current_stamina):
    missing = max_stamina - current_stamina
    minutes_to_full = missing * 8
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)  
    full_time = now + datetime.timedelta(minutes=minutes_to_full)
    return missing, full_time
