"""Real-time problem extractor for ArchiMate architecture attempts."""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path


class ProblemExtractor:
    """Extract and analyze problems from real-time architecture creation attempts."""
    
    def __init__(self, logs_dir: str = "/Users/patrik/Projects/archi-mcp/logs"):
        """Initialize problem extractor.
        
        Args:
            logs_dir: Directory containing validation logs
        """
        self.logs_dir = Path(logs_dir)
        self.validation_log_path = self.logs_dir / "validation_errors.jsonl"
        self.last_check_time = time.time()
        
    def extract_new_problems(self, since_minutes: int = 5) -> Dict[str, Any]:
        """Extract problems from recent validation attempts.
        
        Args:
            since_minutes: Look for problems from last N minutes
            
        Returns:
            Analysis of new problems found
        """
        cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
        
        new_errors = []
        if self.validation_log_path.exists():
            with open(self.validation_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        error_data = json.loads(line.strip())
                        error_time = datetime.fromisoformat(error_data.get('timestamp', ''))
                        
                        if error_time >= cutoff_time:
                            new_errors.append(error_data)
                    except (json.JSONDecodeError, ValueError):
                        continue
        
        return self._analyze_problems(new_errors, since_minutes)
    
    def extract_latest_attempt_problems(self) -> Dict[str, Any]:
        """Extract problems from the most recent architecture attempt.
        
        Returns:
            Analysis of latest attempt problems
        """
        latest_errors = []
        latest_timestamp = None
        
        if self.validation_log_path.exists():
            with open(self.validation_log_path, 'r', encoding='utf-8') as f:
                all_lines = list(f)
                
                # Find the most recent timestamp
                for line in reversed(all_lines):
                    try:
                        error_data = json.loads(line.strip())
                        timestamp_str = error_data.get('timestamp', '')
                        if timestamp_str:
                            latest_timestamp = datetime.fromisoformat(timestamp_str)
                            break
                    except (json.JSONDecodeError, ValueError):
                        continue
                
                if latest_timestamp:
                    # Collect all errors from the same session (within 1 minute of latest)
                    session_cutoff = latest_timestamp - timedelta(minutes=1)
                    
                    for line in all_lines:
                        try:
                            error_data = json.loads(line.strip())
                            error_time = datetime.fromisoformat(error_data.get('timestamp', ''))
                            
                            if error_time >= session_cutoff:
                                latest_errors.append(error_data)
                        except (json.JSONDecodeError, ValueError):
                            continue
        
        return self._analyze_problems(latest_errors, "latest_attempt")
    
    def _analyze_problems(self, errors: List[Dict[str, Any]], timeframe: Any) -> Dict[str, Any]:
        """Analyze a list of validation errors.
        
        Args:
            errors: List of error data dictionaries
            timeframe: Time period description
            
        Returns:
            Comprehensive problem analysis
        """
        if not errors:
            return {
                "timeframe": str(timeframe),
                "total_errors": 0,
                "error_types": {},
                "critical_issues": [],
                "recommendations": ["No recent errors found - system appears stable"],
                "summary": "No problems detected in recent attempts"
            }
        
        analysis = {
            "timeframe": str(timeframe),
            "total_errors": len(errors),
            "error_types": {},
            "tools_with_errors": {},
            "critical_issues": [],
            "pattern_analysis": {},
            "recommendations": [],
            "sample_errors": [],
            "summary": ""
        }
        
        # Categorize errors by type
        for error in errors:
            error_type = error.get('error_type', 'UNKNOWN')
            tool_name = error.get('tool_name', 'unknown')
            
            # Count error types
            analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
            
            # Count tools with errors
            analysis["tools_with_errors"][tool_name] = analysis["tools_with_errors"].get(tool_name, 0) + 1
        
        # Analyze patterns
        analysis["pattern_analysis"] = self._analyze_error_patterns(errors)
        
        # Identify critical issues
        analysis["critical_issues"] = self._identify_critical_issues(errors, analysis["error_types"])
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        # Select sample errors for detailed review
        analysis["sample_errors"] = self._select_sample_errors(errors)
        
        # Generate summary
        analysis["summary"] = self._generate_summary(analysis)
        
        return analysis
    
    def _analyze_error_patterns(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in the errors.
        
        Args:
            errors: List of error data
            
        Returns:
            Pattern analysis results
        """
        patterns = {
            "common_plantuml_issues": [],
            "element_type_problems": [],
            "relationship_issues": [],
            "syntax_patterns": []
        }
        
        for error in errors:
            error_message = error.get('error_message', '')
            plantuml_code = error.get('plantuml_code', '')
            
            # Look for common PlantUML issues
            if 'syntax check failed' in error_message.lower():
                patterns["common_plantuml_issues"].append("PlantUML syntax validation failure")
            
            if 'missing archimate include' in error_message.lower():
                patterns["common_plantuml_issues"].append("Missing ArchiMate include directive")
            
            # Look for element type problems
            if plantuml_code:
                # Check for potential element naming issues
                if 'Business_Business' in plantuml_code or 'Application_Application' in plantuml_code:
                    patterns["element_type_problems"].append("Double layer prefix in element types")
                
                # Check for missing underscores
                if any(f'{layer}Actor' in plantuml_code or f'{layer}Service' in plantuml_code 
                       for layer in ['Business', 'Application', 'Technology']):
                    patterns["element_type_problems"].append("Missing underscores in element types")
            
            # Look for relationship issues
            if 'Rel_' in plantuml_code and 'failed' in error_message.lower():
                patterns["relationship_issues"].append("Relationship syntax or validation error")
        
        # Remove duplicates
        for key in patterns:
            patterns[key] = list(set(patterns[key]))
        
        return patterns
    
    def _identify_critical_issues(self, errors: List[Dict[str, Any]], error_types: Dict[str, int]) -> List[Dict[str, Any]]:
        """Identify critical issues that need immediate attention.
        
        Args:
            errors: List of error data
            error_types: Error type counts
            
        Returns:
            List of critical issues
        """
        critical_issues = []
        
        # High error count is critical
        if len(errors) > 10:
            critical_issues.append({
                "issue": "High Error Volume",
                "severity": "critical",
                "description": f"{len(errors)} validation errors in recent attempt",
                "recommendation": "Review element type normalization and PlantUML generation logic"
            })
        
        # Syntax errors are critical
        syntax_errors = error_types.get('SYNTAX_ERROR', 0)
        if syntax_errors > 0:
            critical_issues.append({
                "issue": "Syntax Errors",
                "severity": "critical", 
                "description": f"{syntax_errors} syntax errors preventing PlantUML generation",
                "recommendation": "Fix basic PlantUML syntax before proceeding"
            })
        
        # High render error rate is critical
        render_errors = error_types.get('RENDER_ERROR', 0)
        if render_errors > 5:
            critical_issues.append({
                "issue": "High Render Error Rate",
                "severity": "critical",
                "description": f"{render_errors} render errors indicate element type problems",
                "recommendation": "Review element normalization and ArchiMate element definitions"
            })
        
        # Missing includes are medium priority
        archimate_errors = error_types.get('ARCHIMATE_ERROR', 0)
        if archimate_errors > 3:
            critical_issues.append({
                "issue": "ArchiMate Include Issues",
                "severity": "medium",
                "description": f"{archimate_errors} missing ArchiMate include directives",
                "recommendation": "Ensure all diagrams include proper ArchiMate headers"
            })
        
        return critical_issues
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis.
        
        Args:
            analysis: Current analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        error_types = analysis["error_types"]
        patterns = analysis["pattern_analysis"]
        
        # Recommendations based on error types
        if error_types.get('RENDER_ERROR', 0) > 0:
            recommendations.append("🔧 Fix element type normalization - run test_element_normalization tool")
            
        if error_types.get('SYNTAX_ERROR', 0) > 0:
            recommendations.append("🚨 Review PlantUML syntax generation - check for empty or malformed code")
            
        if error_types.get('ARCHIMATE_ERROR', 0) > 0:
            recommendations.append("📋 Ensure ArchiMate include directives in all generated diagrams")
        
        # Recommendations based on patterns
        if patterns["element_type_problems"]:
            recommendations.append("🏷️ Review element factory methods - check for double normalization")
            
        if patterns["relationship_issues"]:
            recommendations.append("🔗 Validate relationship definitions and endpoint element existence")
        
        # General recommendations
        if analysis["total_errors"] > 5:
            recommendations.append("📊 Use analyze_current_architecture tool to inspect generator state")
            recommendations.append("🧪 Test individual components before creating complex architectures")
        
        if not recommendations:
            recommendations.append("✅ No specific issues identified - architecture generation appears stable")
        
        return recommendations
    
    def _select_sample_errors(self, errors: List[Dict[str, Any]], max_samples: int = 3) -> List[Dict[str, Any]]:
        """Select representative sample errors for detailed review.
        
        Args:
            errors: List of all errors
            max_samples: Maximum number of samples to return
            
        Returns:
            Sample errors for review
        """
        if not errors:
            return []
        
        # Group errors by type
        error_groups = {}
        for error in errors:
            error_type = error.get('error_type', 'UNKNOWN')
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # Select one sample from each error type
        samples = []
        for error_type, error_list in error_groups.items():
            if len(samples) < max_samples:
                # Select the most recent error of this type
                sample = max(error_list, key=lambda e: e.get('timestamp', ''))
                samples.append({
                    "error_type": error_type,
                    "timestamp": sample.get('timestamp'),
                    "error_message": sample.get('error_message', '')[:200] + "..." if len(sample.get('error_message', '')) > 200 else sample.get('error_message', ''),
                    "tool_name": sample.get('tool_name', 'unknown'),
                    "plantuml_sample": sample.get('plantuml_code', '')[:300] + "..." if len(sample.get('plantuml_code', '')) > 300 else sample.get('plantuml_code', '')
                })
        
        return samples
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a summary of the analysis.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Summary string
        """
        total_errors = analysis["total_errors"]
        
        if total_errors == 0:
            return "✅ No problems detected - architecture generation is working well"
        
        error_types = analysis["error_types"]
        critical_count = len([issue for issue in analysis["critical_issues"] if issue.get("severity") == "critical"])
        
        # Determine overall severity
        if critical_count > 0:
            severity = "🚨 CRITICAL"
        elif total_errors > 5:
            severity = "⚠️ HIGH"
        elif total_errors > 2:
            severity = "⚠️ MEDIUM"
        else:
            severity = "ℹ️ LOW"
        
        # Most common error type
        most_common_error = max(error_types.items(), key=lambda x: x[1]) if error_types else ("NONE", 0)
        
        summary = f"{severity} - {total_errors} errors detected. Most common: {most_common_error[0]} ({most_common_error[1]} occurrences)"
        
        if critical_count > 0:
            summary += f". {critical_count} critical issues require immediate attention."
        
        return summary


# Global problem extractor instance
problem_extractor = ProblemExtractor()


def extract_recent_problems(minutes: int = 5) -> Dict[str, Any]:
    """Extract problems from recent validation attempts.
    
    Args:
        minutes: Look back this many minutes
        
    Returns:
        Problem analysis
    """
    return problem_extractor.extract_new_problems(minutes)


def extract_latest_problems() -> Dict[str, Any]:
    """Extract problems from the latest architecture attempt.
    
    Returns:
        Problem analysis of latest attempt
    """
    return problem_extractor.extract_latest_attempt_problems()