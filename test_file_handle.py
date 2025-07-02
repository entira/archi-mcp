import tempfile
import subprocess
import os

plantuml_jar = '/Users/patrik/Projects/archi-mcp/plantuml.jar'

puml_content = '''@startuml
!include <archimate/Archimate>

title Technology Test

Technology_Node(test_node, "Test Node")

@enduml'''

print('Testing file handle management...')

# Method 1: Current server approach (file handle open during PlantUML call)
print('Method 1: File handle open during PlantUML call')
with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as temp_puml:
    temp_puml.write(puml_content)
    temp_puml_path = temp_puml.name
    
    # PlantUML called while file handle is still open!
    result1 = subprocess.run([
        'java', '-Djava.awt.headless=true', '-jar', plantuml_jar,
        '-tpng', temp_puml_path
    ], capture_output=True, text=True, timeout=10)

print(f'Return code: {result1.returncode}')
if result1.returncode != 0:
    print(f'Error: {result1.stderr.strip()}')
else:
    print('SUCCESS!')

os.unlink(temp_puml_path)

# Method 2: Proper file handle closure
print('\nMethod 2: File handle properly closed')
with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as temp_puml:
    temp_puml.write(puml_content)
    temp_puml_path2 = temp_puml.name
# File handle is now properly closed

result2 = subprocess.run([
    'java', '-Djava.awt.headless=true', '-jar', plantuml_jar,
    '-tpng', temp_puml_path2
], capture_output=True, text=True, timeout=10)

print(f'Return code: {result2.returncode}')
if result2.returncode != 0:
    print(f'Error: {result2.stderr.strip()}')
else:
    print('SUCCESS!')

os.unlink(temp_puml_path2)