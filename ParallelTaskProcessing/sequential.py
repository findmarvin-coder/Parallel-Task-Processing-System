import time

def run_sequential(data):
    """Process the dataset sequentially on a single thread."""
    start_time = time.time()
    
    if not data:
        return {"total": 0, "average": 0, "min": 0, "max": 0, "even": 0, "odd": 0, "time": 0}

    total = sum(data)
    avg = total / len(data)
    min_val = min(data)
    max_val = max(data)
    
    even = sum(1 for x in data if x % 2 == 0)
    odd = len(data) - even
    
    end_time = time.time()

    return {
        "total": total,
        "average": avg,
        "min": min_val,
        "max": max_val,
        "even": even,
        "odd": odd,
        "time": end_time - start_time
    }