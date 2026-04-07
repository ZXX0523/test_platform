---
name: "learning-situation-cleaner"
description: "Clears learning situation data by marking it as deleted. Invoke when user needs to clean up learning situation data for specific students and nodes."
---

# Learning Situation Cleaner

This skill provides functionality to clean up learning situation data by marking it as deleted (is_deleted=1) instead of actually deleting it. It also handles related intervention task data if present.

## Features

- Clears learning situation data for specified student IDs and node IDs
- Marks data as deleted (is_deleted=1) instead of actual deletion
- Handles multiple node IDs in a single API call
- Also cleans up related intervention task data if intervention_task_id is not 0
- Provides a user interface for easy operation

## Implementation Details

### Backend Implementation

1. **dm_script.py** - Added `clear_learning_situation_data` method:
   - Takes parameters: `choose_url` (environment), `student_id`, `node_ids` (comma-separated string)
   - Queries learning situation data for each node ID
   - Marks data as deleted if found
   - Also marks related intervention task data as deleted if intervention_task_id is not 0
   - Returns a summary of operations

2. **dm.py** - Added route for API access:
   - Endpoint: `/dm_gubi/py/clear_learning_situation_data`
   - Accepts parameters: `env`, `student_id`, `node_ids`
   - Returns JSON response with operation results

### Frontend Implementation

1. **dm_gubi.html** - Added UI form:
   - Added "清理学习情况数据" tab
   - Added form with student ID input and node ID checkboxes
   - Implemented custom styled checkboxes for better user experience

2. **dm_gubi.js** - Added JavaScript function:
   - `ClearLearningSituationData()` function handles form submission
   - Collects selected node IDs
   - Sends single API request with comma-separated node IDs
   - Displays operation results

## Usage

1. Open the DM system operation center
2. Select "清理学习情况数据" tab
3. Enter the student ID
4. Select one or more node IDs (首课节点, 首节节点, 首月节点)
5. Choose the environment (UAT or pre-production)
6. Click "确认清理数据" button
7. View the operation results in the result area

## API Usage

**Endpoint:** `/dm_gubi/py/clear_learning_situation_data`

**Parameters:**
- `env`: Environment (test or preprod)
- `student_id`: Student ID
- `node_ids`: Comma-separated list of node IDs (e.g., "1,2,3")

**Response:**
- JSON object with operation results
- Example: `{"msg": "成功清理2个节点，0个节点未找到数据。详细信息：节点1: 操作成功; 节点3: 操作成功", "code": 200, "data": null}`

## Example Use Case

To clear learning situation data for student ID 17510988 for nodes 1 (首课节点) and 3 (首月节点) in the test environment:

1. Access the UI form
2. Enter "17510988" in the student ID field
3. Check the checkboxes for "首课节点" and "首月节点"
4. Select "UAT环境"
5. Click "确认清理数据"
6. View the results in the result area