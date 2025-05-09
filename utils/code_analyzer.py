"""
Code Analyzer for Java Code
This module provides functions to analyze Java code without requiring external ML models.
"""
import re
import os
from typing import Dict, List, Any, Set, Optional
import json

class CodeAnalyzer:
    """
    A class to analyze Java code for various metrics and patterns.
    Designed to work completely offline without external ML models.
    """
    
    def __init__(self):
        # Common code quality issues to look for
        self.code_smells = {
            "long_method": {
                "pattern": r"(?:public|private|protected)\s+(?:static\s+)?(?:\w+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+\s*)?{(?:[^{}]|{[^{}]*})*}",
                "threshold": 30,  # lines
                "description": "Methods with too many lines may be doing too much and should be refactored."
            },
            "too_many_parameters": {
                "pattern": r"(?:public|private|protected)\s+(?:static\s+)?(?:\w+)\s+(\w+)\s*\(([^)]*)\)",
                "threshold": 5,  # parameters
                "description": "Methods with too many parameters are hard to use and understand."
            },
            "catch_exception": {
                "pattern": r"catch\s*\(\s*Exception\s+\w+\s*\)",
                "description": "Catching generic exceptions is usually bad practice."
            },
            "public_fields": {
                "pattern": r"public\s+(?:static\s+)?(?:final\s+)?(?!class|interface|enum)(\w+)\s+(\w+)",
                "description": "Public fields violate encapsulation. Consider using getters/setters."
            },
            "magic_numbers": {
                "pattern": r"(?:=|return|[,(+\-*/])\s*(-?\d+(?:\.\d+)?)\s*(?:[;,)]|$)",
                "exclude": r"(?:0|1|-1|100)",  # Common acceptable "magic" numbers
                "description": "Magic numbers should be replaced with named constants."
            },
            "todo_comments": {
                "pattern": r"//\s*TODO|/\*\s*TODO",
                "description": "TODO comments indicate incomplete code that needs attention."
            },
            "empty_catch": {
                "pattern": r"catch\s*\([^)]+\)\s*{\s*}",
                "description": "Empty catch blocks suppress exceptions without handling them."
            },
            "complex_conditional": {
                "pattern": r"if\s*\([^{]+(&&|\|\|)[^{]+(&&|\|\|)",
                "description": "Complex conditionals can be difficult to understand. Consider simplifying."
            }
        }
        
        # Security issues to look for
        self.security_issues = {
            "sql_injection": {
                "pattern": r'(?:executeQuery|executeUpdate|execute|prepareStatement)\s*\(\s*"[^"]*\+',
                "description": "Potential SQL injection vulnerability. Use prepared statements with parameters."
            },
            "hardcoded_credentials": {
                "pattern": r'(?:password|pwd|passwd|secret|key)\s*=\s*"[^"]{3,}"',
                "description": "Hardcoded credentials are a security risk. Use secure configuration methods."
            },
            "insecure_randoms": {
                "pattern": r'new\s+Random\s*\(',
                "description": "java.util.Random is not cryptographically secure. Use SecureRandom for security purposes."
            },
            "xxe_vulnerability": {
                "pattern": r'(?:DocumentBuilderFactory|SAXParserFactory|XMLInputFactory)',
                "description": "Potential XXE vulnerability. Enable secure processing and disable external entities."
            },
            "log_injection": {
                "pattern": r'log(?:ger)?\.(?:debug|info|warning|error|severe)\s*\([^)]*\+\s*(?:\w+)',
                "description": "Potential log injection. Sanitize user input before logging."
            }
        }
        
        # Performance issues
        self.performance_issues = {
            "string_concatenation_in_loop": {
                "pattern": r'for\s*\([^{]+\{\s*(?:[^;]*;\s*)*\w+\s*\+=\s*"[^"]*"',
                "description": "String concatenation in loops is inefficient. Use StringBuilder instead."
            },
            "instantiation_in_loop": {
                "pattern": r'for\s*\([^{]+\{\s*(?:[^;]*;\s*)*new\s+\w+',
                "description": "Object instantiation inside loops can be inefficient. Consider moving outside the loop."
            },
            "inefficient_string_conversion": {
                "pattern": r'new\s+String\s*\(\s*(""|[^)]+\.toString\(\))',
                "description": "Inefficient string conversion. Use the string directly or the toString() result."
            }
        }
        
        # Design patterns to detect
        self.design_patterns = {
            "singleton": {
                "pattern": r'private\s+static\s+\w+\s+\w+Instance.*?private\s+\w+\s*\(.*?public\s+static\s+\w+\s+getInstance',
                "description": "Singleton pattern: A class with a single instance that provides global access."
            },
            "factory_method": {
                "pattern": r'(?:public|protected)\s+\w+\s+create\w+\s*\([^)]*\)',
                "description": "Factory Method pattern: Creates objects without specifying the exact class to create."
            },
            "observer": {
                "pattern": r'(?:implements|extends)\s+(?:\w+\.)*(?:Observer|Listener)',
                "description": "Observer pattern: Defines one-to-many dependency between objects."
            },
            "builder": {
                "pattern": r'class\s+\w+Builder.*?public\s+\w+\s+build\s*\(',
                "description": "Builder pattern: Separates object construction from its representation."
            },
            "decorator": {
                "pattern": r'class\s+\w+(?:Decorator|Wrapper).*?implements\s+\w+.*?private\s+\w+\s+wrapped',
                "description": "Decorator pattern: Attaches additional responsibilities to objects dynamically."
            }
        }
    
    def analyze_file(self, file_content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single Java file
        
        Args:
            file_content: The content of the Java file
            file_path: Path to the Java file
            
        Returns:
            A dictionary containing analysis results
        """
        results = {
            "file_path": file_path,
            "metrics": self._calculate_metrics(file_content),
            "code_smells": self._detect_code_smells(file_content),
            "security_issues": self._detect_security_issues(file_content),
            "performance_issues": self._detect_performance_issues(file_content),
            "design_patterns": self._detect_design_patterns(file_content),
            "complexity": self._estimate_complexity(file_content)
        }
        
        return results
    
    def analyze_folder(self, folder_path: str, java_files: List[Dict]) -> Dict[str, Any]:
        """
        Analyze all Java files in a folder
        
        Args:
            folder_path: Path to the folder
            java_files: List of dictionaries containing file paths and contents
            
        Returns:
            A dictionary containing aggregated analysis results
        """
        all_results = []
        all_metrics = {
            "total_files": 0,
            "total_lines": 0,
            "total_classes": 0,
            "total_methods": 0,
            "avg_complexity": 0,
            "total_code_smells": 0,
            "total_security_issues": 0,
            "total_performance_issues": 0,
            "detected_design_patterns": set()
        }
        
        # Process each file
        for file_info in java_files:
            if file_info["file_path"].startswith(folder_path):
                file_content = file_info["content"]
                file_result = self.analyze_file(file_content, file_info["file_path"])
                all_results.append(file_result)
                
                # Aggregate metrics
                all_metrics["total_files"] += 1
                all_metrics["total_lines"] += file_result["metrics"]["total_lines"]
                all_metrics["total_classes"] += file_result["metrics"]["class_count"]
                all_metrics["total_methods"] += file_result["metrics"]["method_count"]
                all_metrics["avg_complexity"] += file_result["complexity"]["cyclomatic_complexity"]
                all_metrics["total_code_smells"] += sum(len(occurrences) for occurrences in file_result["code_smells"].values())
                all_metrics["total_security_issues"] += sum(len(occurrences) for occurrences in file_result["security_issues"].values())
                all_metrics["total_performance_issues"] += sum(len(occurrences) for occurrences in file_result["performance_issues"].values())
                
                # Add detected design patterns
                for pattern, occurrences in file_result["design_patterns"].items():
                    if occurrences:
                        all_metrics["detected_design_patterns"].add(pattern)
        
        # Calculate averages
        if all_metrics["total_files"] > 0:
            all_metrics["avg_complexity"] /= all_metrics["total_files"]
            all_metrics["code_smell_density"] = all_metrics["total_code_smells"] / all_metrics["total_lines"] if all_metrics["total_lines"] > 0 else 0
        
        # Convert set to list for JSON serialization
        all_metrics["detected_design_patterns"] = list(all_metrics["detected_design_patterns"])
        
        return {
            "folder_path": folder_path,
            "metrics": all_metrics,
            "file_results": all_results
        }
    
    def _calculate_metrics(self, code: str) -> Dict[str, int]:
        """Calculate basic metrics for a Java file"""
        lines = code.split('\n')
        
        # Count lines
        total_lines = len(lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('/*'))
        comment_lines = sum(1 for line in lines if line.strip().startswith('//') or line.strip().startswith('/*'))
        
        # Count classes and interfaces
        class_count = len(re.findall(r'class\s+\w+', code))
        interface_count = len(re.findall(r'interface\s+\w+', code))
        
        # Count methods
        method_count = len(re.findall(r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+)\s+(\w+)\s*\([^)]*\)', code))
        
        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "class_count": class_count,
            "interface_count": interface_count,
            "method_count": method_count
        }
    
    def _detect_code_smells(self, code: str) -> Dict[str, List[Dict]]:
        """Detect code smells in Java code"""
        results = {}
        
        for smell_name, smell_info in self.code_smells.items():
            pattern = smell_info["pattern"]
            
            if smell_name == "long_method":
                # Special handling for long methods
                matches = re.finditer(pattern, code)
                results[smell_name] = []
                
                for match in matches:
                    method_body = match.group(0)
                    method_name = match.group(1)
                    line_count = method_body.count('\n')
                    
                    if line_count > smell_info["threshold"]:
                        results[smell_name].append({
                            "name": method_name,
                            "lines": line_count,
                            "threshold": smell_info["threshold"],
                            "description": smell_info["description"]
                        })
            
            elif smell_name == "too_many_parameters":
                # Special handling for methods with too many parameters
                matches = re.finditer(pattern, code)
                results[smell_name] = []
                
                for match in matches:
                    method_name = match.group(1)
                    params = match.group(2).strip()
                    
                    if not params:
                        param_count = 0
                    else:
                        param_count = len(params.split(','))
                    
                    if param_count > smell_info["threshold"]:
                        results[smell_name].append({
                            "name": method_name,
                            "parameter_count": param_count,
                            "threshold": smell_info["threshold"],
                            "description": smell_info["description"]
                        })
            
            elif smell_name == "magic_numbers":
                # Special handling for magic numbers
                matches = re.finditer(pattern, code)
                results[smell_name] = []
                exclude_pattern = smell_info.get("exclude", r"$^")  # Never match by default
                
                for match in matches:
                    number = match.group(1)
                    # Skip excluded numbers
                    if not re.match(exclude_pattern, number):
                        results[smell_name].append({
                            "number": number,
                            "description": smell_info["description"]
                        })
            
            else:
                # General handling for other code smells
                matches = re.finditer(pattern, code)
                results[smell_name] = []
                
                for match in matches:
                    results[smell_name].append({
                        "match": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        "description": smell_info["description"]
                    })
        
        return results
    
    def _detect_security_issues(self, code: str) -> Dict[str, List[Dict]]:
        """Detect security issues in Java code"""
        results = {}
        
        for issue_name, issue_info in self.security_issues.items():
            pattern = issue_info["pattern"]
            
            matches = re.finditer(pattern, code)
            results[issue_name] = []
            
            for match in matches:
                results[issue_name].append({
                    "match": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                    "description": issue_info["description"]
                })
        
        return results
    
    def _detect_performance_issues(self, code: str) -> Dict[str, List[Dict]]:
        """Detect performance issues in Java code"""
        results = {}
        
        for issue_name, issue_info in self.performance_issues.items():
            pattern = issue_info["pattern"]
            
            matches = re.finditer(pattern, code)
            results[issue_name] = []
            
            for match in matches:
                results[issue_name].append({
                    "match": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                    "description": issue_info["description"]
                })
        
        return results
    
    def _detect_design_patterns(self, code: str) -> Dict[str, List[Dict]]:
        """Detect design patterns in Java code"""
        results = {}
        
        for pattern_name, pattern_info in self.design_patterns.items():
            pattern = pattern_info["pattern"]
            
            try:
                matches = re.finditer(pattern, code, re.DOTALL)
                results[pattern_name] = []
                
                for match in matches:
                    results[pattern_name].append({
                        "match": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        "description": pattern_info["description"]
                    })
            except:
                # If regex fails, continue with empty results
                results[pattern_name] = []
        
        return results
    
    def _estimate_complexity(self, code: str) -> Dict[str, Any]:
        """Estimate code complexity"""
        # Count decision points (branching)
        if_count = len(re.findall(r'\bif\s*\(', code))
        else_count = len(re.findall(r'\belse\b', code))
        for_count = len(re.findall(r'\bfor\s*\(', code))
        while_count = len(re.findall(r'\bwhile\s*\(', code))
        case_count = len(re.findall(r'\bcase\s+', code))
        catch_count = len(re.findall(r'\bcatch\s*\(', code))
        
        # Calculate cyclomatic complexity (approximation)
        # Each branching point adds 1 to complexity
        # 1 is the base complexity for a linear path
        cyclomatic_complexity = 1 + if_count + else_count + for_count + while_count + case_count + catch_count
        
        # Assess cognitive complexity
        cognitive_score = cyclomatic_complexity
        nested_blocks = 0
        lines = code.split('\n')
        
        indent_level = 0
        max_indent = 0
        
        # Estimate nesting depth by tracking indentation
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            if stripped.startswith('}'):
                indent_level -= 1
            
            current_indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent_level)
            
            if stripped.endswith('{'):
                indent_level += 1
        
        # Apply nesting penalty to cognitive complexity
        cognitive_score += max_indent * 2
        
        # Complexity rating
        if cyclomatic_complexity <= 5:
            rating = "Low"
        elif cyclomatic_complexity <= 10:
            rating = "Moderate"
        elif cyclomatic_complexity <= 20:
            rating = "High" 
        else:
            rating = "Very High"
            
        return {
            "cyclomatic_complexity": cyclomatic_complexity,
            "cognitive_complexity": cognitive_score,
            "max_nesting_depth": max_indent,
            "branches": {
                "if": if_count,
                "else": else_count,
                "for": for_count,
                "while": while_count,
                "case": case_count,
                "catch": catch_count
            },
            "complexity_rating": rating
        }