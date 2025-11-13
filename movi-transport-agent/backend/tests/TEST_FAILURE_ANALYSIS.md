cd /Users/radhikakulkarni/Downloads/30days_challenge/assignment_for_moveinsync/movi-transport-agent && python3 -c "
import re
file_path = 'backend/app/tools/create_tools.py'
with open(file_path, 'r') as f:
   content = f.read()


pattern = r'(# Insert deployment record\s+deployment = 
Deployment\(\s+trip_id=trip\.trip_id,\s+vehicle_id=vehicle\.vehicle_id,)'

replacement = r'''# Get first available driver
         available_driver = db.query(Driver).outerjoin(
            Deployment
         ).filter(
            Deployment.driver_id.is_(None)
         ).first()
         
         if not available_driver:
            # If no unassigned drivers, use any driver
            available_driver = db.query(Driver).first()
         
         if not available_driver:
            return error_response('No drivers available in the system')
         
         \1
            driver_id=available_driver.driver_id,'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)
with open(file_path, 'w') as f:
   f.write(content)
print('✅ Fixed assign_vehicle_to_trip to include driver_id')
" && python3 backend/tests/test_all_tools_v2.py
