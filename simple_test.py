from prometheus_client import Counter, generate_latest

# Create a simple counter
test_counter = Counter('test_counter', 'A test counter')

# Increment it
test_counter.inc()

# Generate metrics
output = generate_latest().decode('utf-8')
print("Metrics output:")
print(output) 