import ast
import re
from typing import List, Dict, Any, Optional, Tuple
import json

from utils.data_models import ClassDefinition, Attribute, Method, Relationship, UMLDiagram


class CodeParser:
    """Base class for code parsers"""
    def parse(self, code: str) -> UMLDiagram:
        raise NotImplementedError("Subclass must implement abstract method")
    

class PythonParser(CodeParser):
    """Parser for Python code"""
    def parse(self, code: str) -> UMLDiagram:
        try:
            tree = ast.parse(code)
            
            classes = []
            relationships = []
            
            class_names = set()
            
            # First pass: collect all class names
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_names.add(node.name)
            
            # Second pass: extract class definitions and relationships
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Class info
                    class_def = ClassDefinition(name=node.name)
                    
                    # Check if class is abstract
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                            class_def.is_abstract = True
                    
                    # Get inheritance relationships
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in class_names:
                            relationships.append(
                                Relationship(
                                    source=node.name,
                                    target=base.id,
                                    type="inheritance"
                                )
                            )
                    
                    # Get attributes and methods
                    for item in node.body:
                        # Get class attributes
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            # Type annotated attribute
                            visibility = "+"
                            if item.target.id.startswith("__"):
                                visibility = "-"
                            elif item.target.id.startswith("_"):
                                visibility = "#"
                            
                            type_name = ""
                            if isinstance(item.annotation, ast.Name):
                                type_name = item.annotation.id
                            elif isinstance(item.annotation, ast.Subscript):
                                if isinstance(item.annotation.value, ast.Name):
                                    type_name = item.annotation.value.id + "[...]"
                            
                            class_def.attributes.append(
                                Attribute(
                                    name=item.target.id,
                                    type=type_name,
                                    visibility=visibility
                                )
                            )
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    visibility = "+"
                                    if target.id.startswith("__"):
                                        visibility = "-"
                                    elif target.id.startswith("_"):
                                        visibility = "#"
                                    
                                    class_def.attributes.append(
                                        Attribute(
                                            name=target.id,
                                            visibility=visibility
                                        )
                                    )
                        
                        # Get methods
                        elif isinstance(item, ast.FunctionDef):
                            visibility = "+"
                            if item.name.startswith("__") and not item.name.endswith("__"):
                                visibility = "-"
                            elif item.name.startswith("_"):
                                visibility = "#"
                            
                            is_static = False
                            is_abstract = False
                            
                            # Check decorators for static/abstract
                            for decorator in item.decorator_list:
                                if isinstance(decorator, ast.Name):
                                    if decorator.id == 'staticmethod':
                                        is_static = True
                                    elif decorator.id == 'abstractmethod':
                                        is_abstract = True
                            
                            # Parse parameters
                            params = []
                            for arg in item.args.args:
                                if arg.arg != 'self' and arg.arg != 'cls':
                                    param_type = ""
                                    if arg.annotation and isinstance(arg.annotation, ast.Name):
                                        param_type = arg.annotation.id
                                    params.append({"name": arg.arg, "type": param_type})
                            
                            # Return type
                            return_type = ""
                            if item.returns:
                                if isinstance(item.returns, ast.Name):
                                    return_type = item.returns.id
                                elif isinstance(item.returns, ast.Constant) and item.returns.value is None:
                                    return_type = "None"
                            
                            class_def.methods.append(
                                Method(
                                    name=item.name,
                                    return_type=return_type,
                                    parameters=params,
                                    visibility=visibility,
                                    is_static=is_static,
                                    is_abstract=is_abstract
                                )
                            )
                    
                    classes.append(class_def)
            
            return UMLDiagram(classes=classes, relationships=relationships)
        
        except Exception as e:
            raise ValueError(f"Error parsing Python code: {str(e)}")


class JavaParser(CodeParser):
    """Parser for Java code"""
    def parse(self, code: str) -> UMLDiagram:
        try:
            classes = []
            relationships = []
            
            # Find class definitions
            class_pattern = r'(public\s+|private\s+|protected\s+|\s*)' + \
                            r'(abstract\s+)?(class|interface)\s+(\w+)' + \
                            r'(\s+extends\s+(\w+))?(\s+implements\s+([^{]+))?'
            
            class_matches = re.finditer(class_pattern, code)
            
            class_names = set()
            
            # First pass - collect class names
            for match in class_matches:
                class_name = match.group(4)
                class_names.add(class_name)
            
            # Reset for second pass
            class_matches = re.finditer(class_pattern, code)
            
            for match in class_matches:
                access = match.group(1).strip()
                is_abstract = match.group(2) is not None
                is_interface = match.group(3) == 'interface'
                class_name = match.group(4)
                
                extends = match.group(6)
                implements = match.group(8)
                
                class_def = ClassDefinition(
                    name=class_name,
                    is_abstract=is_abstract,
                    is_interface=is_interface
                )
                
                # Add inheritance relationships
                if extends and extends in class_names:
                    relationships.append(
                        Relationship(
                            source=class_name,
                            target=extends,
                            type="inheritance"
                        )
                    )
                
                if implements:
                    for interface in [i.strip() for i in implements.split(',')]:
                        if interface in class_names:
                            relationships.append(
                                Relationship(
                                    source=class_name,
                                    target=interface,
                                    type="implementation"
                                )
                            )
                
                # Find the class body
                class_start = code.find('{', code.find(class_name))
                if class_start == -1:
                    continue
                
                # Balance brackets to find the end of the class
                bracket_count = 1
                class_end = class_start + 1
                
                while bracket_count > 0 and class_end < len(code):
                    if code[class_end] == '{':
                        bracket_count += 1
                    elif code[class_end] == '}':
                        bracket_count -= 1
                    class_end += 1
                
                class_body = code[class_start+1:class_end-1]
                
                # Find attributes
                attr_pattern = r'(public|private|protected)?\s+(static\s+)?(final\s+)?' + \
                               r'(\w+)\s+(\w+)\s*(?:=\s*[^;]+)?;'
                
                for attr_match in re.finditer(attr_pattern, class_body):
                    visibility = "+"
                    if attr_match.group(1) == "private":
                        visibility = "-"
                    elif attr_match.group(1) == "protected":
                        visibility = "#"
                    
                    is_static = attr_match.group(2) is not None
                    attr_type = attr_match.group(4)
                    attr_name = attr_match.group(5)
                    
                    class_def.attributes.append(
                        Attribute(
                            name=attr_name,
                            type=attr_type,
                            visibility=visibility,
                            is_static=is_static
                        )
                    )
                
                # Find methods
                method_pattern = r'(public|private|protected)?\s+(static\s+)?(abstract\s+)?' + \
                                r'(\w+)\s+(\w+)\s*\((.*?)\)\s*(?:\{|;)'
                
                for method_match in re.finditer(method_pattern, class_body):
                    visibility = "+"
                    if method_match.group(1) == "private":
                        visibility = "-"
                    elif method_match.group(1) == "protected":
                        visibility = "#"
                    
                    is_static = method_match.group(2) is not None
                    is_abstract = method_match.group(3) is not None
                    return_type = method_match.group(4)
                    method_name = method_match.group(5)
                    params_str = method_match.group(6).strip()
                    
                    params = []
                    if params_str:
                        param_list = params_str.split(',')
                        for param in param_list:
                            param = param.strip()
                            if ' ' in param:
                                param_parts = param.split(' ')
                                param_type = param_parts[0]
                                param_name = param_parts[1]
                                params.append({"name": param_name, "type": param_type})
                    
                    class_def.methods.append(
                        Method(
                            name=method_name,
                            return_type=return_type,
                            parameters=params,
                            visibility=visibility,
                            is_static=is_static,
                            is_abstract=is_abstract
                        )
                    )
                
                classes.append(class_def)
            
            return UMLDiagram(classes=classes, relationships=relationships)
            
        except Exception as e:
            raise ValueError(f"Error parsing Java code: {str(e)}")


class JavaScriptParser(CodeParser):
    """Parser for JavaScript code"""
    def parse(self, code: str) -> UMLDiagram:
        try:
            classes = []
            relationships = []
            
            # Find ES6 class definitions
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
            
            class_matches = re.finditer(class_pattern, code)
            
            for match in class_matches:
                class_name = match.group(1)
                extends = match.group(2)
                
                class_def = ClassDefinition(name=class_name)
                
                # Add inheritance relationships
                if extends:
                    relationships.append(
                        Relationship(
                            source=class_name,
                            target=extends,
                            type="inheritance"
                        )
                    )
                
                # Find the class body
                class_start = code.find('{', match.start())
                if class_start == -1:
                    continue
                
                # Balance brackets to find the end of the class
                bracket_count = 1
                class_end = class_start + 1
                
                while bracket_count > 0 and class_end < len(code):
                    if code[class_end] == '{':
                        bracket_count += 1
                    elif code[class_end] == '}':
                        bracket_count -= 1
                    class_end += 1
                
                class_body = code[class_start+1:class_end-1]
                
                # Find class methods
                # Match constructor, normal methods and getters/setters
                method_pattern = r'(?:static\s+)?(?:async\s+)?(?:get|set|constructor|\w+)\s*\([^)]*\)\s*\{'
                
                current_pos = 0
                for method_match in re.finditer(method_pattern, class_body):
                    method_def = method_match.group(0)
                    
                    is_static = 'static' in method_def
                    
                    # Extract method name
                    if 'constructor' in method_def:
                        method_name = 'constructor'
                    else:
                        name_match = re.search(r'(?:static\s+)?(?:async\s+)?(?:get|set|\w+)', method_def)
                        if name_match:
                            method_name = name_match.group(0)
                            if 'static' in method_name:
                                method_name = method_name.replace('static', '').strip()
                            if 'async' in method_name:
                                method_name = method_name.replace('async', '').strip()
                        else:
                            continue
                    
                    # Extract parameters
                    params = []
                    params_match = re.search(r'\((.*?)\)', method_def)
                    if params_match:
                        params_str = params_match.group(1)
                        if params_str:
                            param_list = params_str.split(',')
                            for param in param_list:
                                param = param.strip()
                                if param and param != '':
                                    # Remove default values
                                    if '=' in param:
                                        param = param.split('=')[0].strip()
                                    params.append({"name": param, "type": ""})
                    
                    class_def.methods.append(
                        Method(
                            name=method_name,
                            parameters=params,
                            visibility="+",  # JavaScript doesn't have explicit visibility
                            is_static=is_static
                        )
                    )
                
                # Find class attributes (from constructor)
                constructor_pattern = r'constructor\s*\([^)]*\)\s*\{([\s\S]*?)(?:\}|$)'
                constructor_match = re.search(constructor_pattern, class_body)
                
                if constructor_match:
                    constructor_body = constructor_match.group(1)
                    # Find this.x = y patterns for attributes
                    attr_pattern = r'this\.(\w+)\s*='
                    
                    for attr_match in re.finditer(attr_pattern, constructor_body):
                        attr_name = attr_match.group(1)
                        class_def.attributes.append(
                            Attribute(
                                name=attr_name,
                                visibility="+",  # JavaScript doesn't have explicit visibility
                            )
                        )
                
                # Find static attributes
                static_attr_pattern = r'static\s+(\w+)\s*='
                for static_attr_match in re.finditer(static_attr_pattern, class_body):
                    attr_name = static_attr_match.group(1)
                    class_def.attributes.append(
                        Attribute(
                            name=attr_name,
                            visibility="+",  # JavaScript doesn't have explicit visibility
                            is_static=True
                        )
                    )
                
                classes.append(class_def)
            
            return UMLDiagram(classes=classes, relationships=relationships)
            
        except Exception as e:
            raise ValueError(f"Error parsing JavaScript code: {str(e)}")


class ManualInputParser:
    """Parser for JSON input containing manual class definitions"""
    def parse(self, json_str: str) -> UMLDiagram:
        try:
            data = json.loads(json_str)
            
            classes = []
            relationships = []
            
            # Parse classes
            for class_data in data.get('classes', []):
                attributes = []
                for attr in class_data.get('attributes', []):
                    attributes.append(Attribute(**attr))
                
                methods = []
                for method in class_data.get('methods', []):
                    methods.append(Method(**method))
                
                class_def = ClassDefinition(
                    name=class_data['name'],
                    attributes=attributes,
                    methods=methods,
                    is_abstract=class_data.get('is_abstract', False),
                    is_interface=class_data.get('is_interface', False),
                    package=class_data.get('package', '')
                )
                
                classes.append(class_def)
            
            # Parse relationships
            for rel in data.get('relationships', []):
                relationships.append(Relationship(**rel))
            
            return UMLDiagram(classes=classes, relationships=relationships)
            
        except Exception as e:
            raise ValueError(f"Error parsing manual input: {str(e)}")


def get_parser(language: str) -> CodeParser:
    """Factory function to get the appropriate parser"""
    parsers = {
        'python': PythonParser(),
        'java': JavaParser(),
        'javascript': JavaScriptParser()
    }
    
    return parsers.get(language.lower(), None)
