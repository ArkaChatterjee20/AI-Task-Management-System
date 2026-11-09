from api_elt_pipeline.validation.validator import validate_tasks
from api_elt_pipeline.validation.deduplication import filter_new_tasks

tasks = [
    {"userId": 1, "id": 101, "title": "Task A", "completed": False},
    {"userId": 1, "id": 102, "title": "Task B", "completed": True},
    {"userId": 1, "id": 101, "title": "Task A duplicate", "completed": False},
    {"userId": 2, "id": 103, "title": "Task C", "completed": True},
]

# Step 1: Validate all records, including duplicates.
validation_result = validate_tasks(tasks)
print("Validation result:", validation_result)

# Step 2: Remove duplicates and previously processed IDs.
processed_ids = {103}
new_tasks = filter_new_tasks(tasks, processed_ids)

print("New task IDs:", [task["id"] for task in new_tasks])
print("New task count:", len(new_tasks))

assert validation_result is True
assert [task["id"] for task in new_tasks] == [101, 102]

print("VALIDATION AND DEDUPLICATION TEST PASSED")
