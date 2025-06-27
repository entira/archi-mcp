"""Enhanced PlantUML validation with detailed error logging."""

import os
import json
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ValidationError:
    """Represents a validation error with context."""
    timestamp: str
    error_type: str
    error_message: str
    plantuml_code: str
    tool_name: str
    context: Dict[str, any] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

class ValidationLogger:
    """Enhanced PlantUML validation with comprehensive error logging."""
    
    def __init__(self, log_dir: str = "/Users/patrik/Projects/archi-mcp/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.validation_log = self.log_dir / "validation_errors.jsonl"
        self.plantuml_samples = self.log_dir / "plantuml_samples"
        self.plantuml_samples.mkdir(exist_ok=True)
        
    def log_validation_error(self, error: ValidationError) -> None:
        """Log validation error to file."""
        try:
            with open(self.validation_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error.to_dict(), ensure_ascii=False) + '\n')
                
            # Save PlantUML sample for analysis
            timestamp_safe = error.timestamp.replace(':', '-').replace(' ', '_')
            sample_file = self.plantuml_samples / f"{error.tool_name}_{timestamp_safe}.puml"
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(error.plantuml_code)
                
        except Exception as e:
            print(f"Failed to log validation error: {e}")
    
    def validate_plantuml_comprehensive(self, plantuml_code: str, tool_name: str = "unknown", context: Dict = None) -> Tuple[bool, str]:
        """
        Comprehensive PlantUML validation with multiple checks and detailed logging.
        Returns (success: bool, error_message: str)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Step 1: Basic syntax validation
        syntax_ok, syntax_msg = self._validate_basic_syntax(plantuml_code)
        if not syntax_ok:
            error = ValidationError(
                timestamp=timestamp,
                error_type="SYNTAX_ERROR",
                error_message=syntax_msg,
                plantuml_code=plantuml_code,
                tool_name=tool_name,
                context=context
            )
            self.log_validation_error(error)
            return False, f"Syntax validation failed: {syntax_msg}"
        
        # Step 2: ArchiMate specific validation
        archimate_ok, archimate_msg = self._validate_archimate_syntax(plantuml_code)
        if not archimate_ok:
            error = ValidationError(
                timestamp=timestamp,
                error_type="ARCHIMATE_ERROR", 
                error_message=archimate_msg,
                plantuml_code=plantuml_code,
                tool_name=tool_name,
                context=context
            )
            self.log_validation_error(error)
            return False, f"ArchiMate validation failed: {archimate_msg}"
        
        # Step 3: PlantUML jar rendering test
        render_ok, render_msg = self._test_plantuml_rendering(plantuml_code)
        if not render_ok:
            error = ValidationError(
                timestamp=timestamp,
                error_type="RENDER_ERROR",
                error_message=render_msg,
                plantuml_code=plantuml_code,
                tool_name=tool_name,
                context=context
            )
            self.log_validation_error(error)
            return False, f"Rendering validation failed: {render_msg}"
        
        # Step 4: Image quality validation
        quality_ok, quality_msg = self._validate_image_quality(plantuml_code)
        if not quality_ok:
            error = ValidationError(
                timestamp=timestamp,
                error_type="QUALITY_ERROR",
                error_message=quality_msg,
                plantuml_code=plantuml_code,
                tool_name=tool_name,
                context=context
            )
            self.log_validation_error(error)
            return False, f"Image quality validation failed: {quality_msg}"
        
        return True, "All validations passed successfully"
    
    def _validate_basic_syntax(self, plantuml_code: str) -> Tuple[bool, str]:
        """Validate basic PlantUML syntax."""
        if not plantuml_code.strip():
            return False, "Empty PlantUML code"
        
        # Check for required @startuml/@enduml
        if "@startuml" not in plantuml_code:
            return False, "Missing @startuml directive"
        
        if "@enduml" not in plantuml_code:
            return False, "Missing @enduml directive"
        
        # Check for common syntax issues
        lines = plantuml_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("'") or line.startswith("!"):
                continue
                
            # Check for invalid characters in element IDs
            if any(char in line for char in [" ", "-"] if line.startswith(("Business_", "Application_", "Technology_", "Motivation_", "Strategy_", "Implementation_"))):
                if "(" in line and "," in line:
                    # Extract element ID
                    try:
                        element_part = line.split("(")[1].split(",")[0]
                        if " " in element_part or "-" in element_part:
                            return False, f"Line {i}: Invalid characters in element ID '{element_part}' - use underscores only"
                    except:
                        pass
        
        return True, "Basic syntax OK"
    
    def _validate_archimate_syntax(self, plantuml_code: str) -> Tuple[bool, str]:
        """Validate ArchiMate-specific syntax."""
        # Check for ArchiMate include
        if "!include <archimate/Archimate>" not in plantuml_code:
            return False, "Missing ArchiMate include directive"
        
        # Check for invalid ArchiMate element types
        invalid_patterns = [
            "Business_Business_",  # Double layer prefix
            "Application_Application_",
            "Technology_Technology_", 
            "business-actor",  # Kebab case instead of underscore
            "application-component",
            "system-software",
            "data-object"
        ]
        
        # Check for valid ArchiMate patterns but exclude certain problematic ones
        problematic_patterns = [
            "Actor(",  # Without layer prefix in element definition context
            "Service(",
            "Component(",
        ]
        
        for pattern in invalid_patterns:
            if pattern in plantuml_code:
                return False, f"Invalid ArchiMate pattern found: '{pattern}'"
        
        # Check for problematic patterns in element definitions only
        lines = plantuml_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("'") or line.startswith("!") or line.startswith("title") or line.startswith("legend"):
                continue
            
            # Only check element definition lines (not relationships)
            if any(line.startswith(prefix) for prefix in ["Business_", "Application_", "Technology_", "Motivation_", "Strategy_", "Implementation_"]):
                for pattern in problematic_patterns:
                    # Check if pattern appears in a standalone context (not part of a valid element type)
                    if pattern in line and not any(valid_prefix + pattern.replace("(", "") in line for valid_prefix in ["Business_", "Application_", "Technology_", "Motivation_", "Strategy_", "Implementation_"]):
                        return False, f"Line {i}: Invalid element pattern '{pattern}' - missing layer prefix"
        
        # Check for required element naming patterns
        lines = plantuml_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if any(line.startswith(prefix) for prefix in ["Business_", "Application_", "Technology_", "Motivation_", "Strategy_", "Implementation_"]):
                # Validate element definition syntax
                if not ("(" in line and ")" in line and "," in line):
                    return False, f"Line {i}: Invalid element definition syntax"
                
                # Check for proper quoting of names with special characters
                if "\"" not in line:
                    return False, f"Line {i}: Element name should be quoted"
        
        return True, "ArchiMate syntax OK"
    
    def _test_plantuml_rendering(self, plantuml_code: str) -> Tuple[bool, str]:
        """Test actual PlantUML rendering with jar."""
        try:
            # Create temporary PlantUML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
                f.write(plantuml_code)
                temp_puml = f.name
            
            try:
                # Find PlantUML jar
                plantuml_jar = None
                possible_locations = [
                    "/Users/patrik/Projects/archi-mcp/plantuml.jar",
                    "./plantuml.jar",
                    "/usr/local/bin/plantuml.jar",
                    "/opt/homebrew/bin/plantuml.jar"
                ]
                
                for jar_path in possible_locations:
                    if os.path.exists(jar_path):
                        plantuml_jar = jar_path
                        break
                
                if not plantuml_jar:
                    return False, "PlantUML jar not found - cannot validate rendering"
                
                # Test both syntax check and actual rendering
                # 1. Syntax check
                check_cmd = [
                    "java", "-jar", plantuml_jar,
                    "-checkonly", "-quiet",
                    temp_puml
                ]
                
                check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=15)
                
                # 2. Actual rendering test
                render_cmd = [
                    "java", "-jar", plantuml_jar,
                    "-tpng", "-quiet",
                    temp_puml
                ]
                
                render_result = subprocess.run(render_cmd, capture_output=True, text=True, timeout=30)
                
                # Check if image was actually generated
                generated_image = Path(temp_puml).parent / f"{Path(temp_puml).stem}.png"
                image_created = generated_image.exists()
                
                # Analyze results
                if check_result.returncode != 0:
                    error_msg = check_result.stderr or check_result.stdout or "Syntax check failed"
                    return False, f"Syntax check failed: {error_msg}"
                
                if render_result.returncode != 0:
                    error_msg = render_result.stderr or render_result.stdout or "Rendering failed"
                    return False, f"Rendering failed: {error_msg}"
                
                if not image_created:
                    return False, "No image file was generated"
                
                # Check image file size
                image_size = generated_image.stat().st_size
                if image_size < 100:  # Very small images likely indicate errors
                    return False, f"Generated image too small ({image_size} bytes) - likely rendering error"
                
                # Clean up generated image
                if generated_image.exists():
                    generated_image.unlink()
                
                return True, f"Successfully rendered {image_size} byte image"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_puml):
                    os.unlink(temp_puml)
                    
        except subprocess.TimeoutExpired:
            return False, "PlantUML rendering timed out - diagram too complex or infinite loop"
        except Exception as e:
            return False, f"Rendering test error: {str(e)}"
    
    def _validate_image_quality(self, plantuml_code: str) -> Tuple[bool, str]:
        """Validate that generated image meets quality standards."""
        # Count elements and relationships for complexity check
        element_count = len([line for line in plantuml_code.split('\n') 
                           if any(line.strip().startswith(prefix) for prefix in 
                                ["Business_", "Application_", "Technology_", "Motivation_", "Strategy_", "Implementation_"])])
        
        relationship_count = len([line for line in plantuml_code.split('\n') 
                                if line.strip().startswith("Rel_")])
        
        # Basic quality checks
        if element_count == 0:
            return False, "No elements found in diagram"
        
        if element_count > 50:
            return False, f"Too many elements ({element_count}) - diagram may be unreadable"
        
        # Check for reasonable element to relationship ratio
        if element_count > 5 and relationship_count == 0:
            return False, "Multiple elements but no relationships - incomplete diagram"
        
        return True, f"Quality OK: {element_count} elements, {relationship_count} relationships"
    
    def get_validation_summary(self) -> Dict[str, any]:
        """Get summary of validation errors."""
        if not self.validation_log.exists():
            return {"total_errors": 0, "errors_by_type": {}, "errors_by_tool": {}}
        
        errors_by_type = {}
        errors_by_tool = {}
        total_errors = 0
        
        try:
            with open(self.validation_log, 'r', encoding='utf-8') as f:
                for line in f:
                    error_data = json.loads(line.strip())
                    total_errors += 1
                    
                    error_type = error_data.get('error_type', 'unknown')
                    tool_name = error_data.get('tool_name', 'unknown')
                    
                    errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
                    errors_by_tool[tool_name] = errors_by_tool.get(tool_name, 0) + 1
        
        except Exception as e:
            print(f"Error reading validation log: {e}")
        
        return {
            "total_errors": total_errors,
            "errors_by_type": errors_by_type,
            "errors_by_tool": errors_by_tool,
            "log_file": str(self.validation_log)
        }

# Global instance
validation_logger = ValidationLogger()