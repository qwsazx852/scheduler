import json

def check():
    with open('config/config_employees.json', 'r') as f:
        emps = json.load(f)
    
    count = 0
    total = len(emps)
    names = []
    
    for e in emps:
        if "A2C" in e.get("allowed_shifts", []):
            count += 1
            names.append(e['name'])
            
    print(f"Total Employees: {total}")
    print(f"Employees allowing 'A2C': {count}")
    if names:
        print(f"Names: {', '.join(names[:5])}...")

if __name__ == "__main__":
    check()
