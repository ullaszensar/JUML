import graphviz
import base64
import io
from typing import List, Dict, Any

from utils.data_models import UMLDiagram, ClassDefinition, Relationship


class UMLGenerator:
    """Generate UML diagrams using Graphviz"""
    
    def __init__(self):
        """Initialize the UML generator"""
        pass
    
    def _format_name(self, name: str) -> str:
        """Format class name for display - no escaping needed"""
        return name
    
    def _format_attribute(self, attr: Dict[str, Any]) -> str:
        """Format a single attribute for display"""
        visibility = attr.get('visibility', '+')
        static = "[static] " if attr.get('is_static', False) else ""
        name = attr.get('name', '')
        type_str = f": {attr.get('type', '')}" if attr.get('type') else ""
        return f"{visibility} {static}{name}{type_str}"
    
    def _format_method(self, method: Dict[str, Any]) -> str:
        """Format a single method for display"""
        visibility = method.get('visibility', '+')
        static = "[static] " if method.get('is_static', False) else ""
        abstract = "[abstract] " if method.get('is_abstract', False) else ""
        name = method.get('name', '')
        
        # Format parameters
        params = []
        for param in method.get('parameters', []):
            param_name = param.get('name', '')
            param_type = f": {param.get('type', '')}" if param.get('type') else ""
            params.append(f"{param_name}{param_type}")
        
        param_str = ", ".join(params)
        return_type = f": {method.get('return_type', '')}" if method.get('return_type') else ""
        
        return f"{visibility} {static}{abstract}{name}({param_str}){return_type}"
    
    def generate(self, uml_diagram: UMLDiagram) -> graphviz.Digraph:
        """Generate a Graphviz diagram using simple non-record labels"""
        dot = graphviz.Digraph(engine='dot', format='svg')
        dot.attr('graph', fontname='Arial', rankdir='TB')
        dot.attr('node', shape='box', style='filled', fillcolor='white', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
        # Create nodes for classes
        for class_def in uml_diagram.classes:
            name = class_def.name
            label_parts = []
            
            # Class name section with stereotypes
            display_name = name
            if class_def.is_interface:
                display_name = f"<<interface>>\n{name}"
            elif class_def.is_abstract:
                display_name = f"<<abstract>>\n{name}"
            
            label_parts.append(display_name)
            
            # Line separator
            label_parts.append("-" * 15)
            
            # Attributes section
            if class_def.attributes:
                for attr in class_def.attributes:
                    attr_text = self._format_attribute(attr.model_dump())
                    label_parts.append(attr_text)
            
            # Line separator
            label_parts.append("-" * 15)
            
            # Methods section
            if class_def.methods:
                for method in class_def.methods:
                    method_text = self._format_method(method.model_dump())
                    label_parts.append(method_text)
            
            # Join all parts with newlines
            label = "\n".join(label_parts)
            
            # Add node to graph
            dot.node(name, label=label)
        
        # Create edges for relationships
        for rel in uml_diagram.relationships:
            source = rel.source
            target = rel.target
            
            edge_attrs = {
                'label': rel.label or '',
                'fontname': 'Arial'
            }
            
            # Set style based on relationship type
            if rel.type == "inheritance":
                edge_attrs['dir'] = 'back'
                edge_attrs['arrowtail'] = 'empty'
                edge_attrs['style'] = 'solid'
            elif rel.type == "implementation":
                edge_attrs['dir'] = 'back'
                edge_attrs['arrowtail'] = 'empty'
                edge_attrs['style'] = 'dashed'
            elif rel.type == "association":
                edge_attrs['dir'] = 'none'
                edge_attrs['style'] = 'solid'
            elif rel.type == "dependency":
                edge_attrs['dir'] = 'forward'
                edge_attrs['arrowhead'] = 'vee'
                edge_attrs['style'] = 'dashed'
            elif rel.type == "aggregation":
                edge_attrs['dir'] = 'back'
                edge_attrs['arrowtail'] = 'odiamond'
                edge_attrs['style'] = 'solid'
            elif rel.type == "composition":
                edge_attrs['dir'] = 'back'
                edge_attrs['arrowtail'] = 'diamond'
                edge_attrs['style'] = 'solid'
            
            # Add multiplicity if specified
            if rel.multiplicity:
                edge_attrs['label'] = rel.multiplicity if not rel.label else f"{rel.label}\n{rel.multiplicity}"
            
            dot.edge(source, target, **edge_attrs)
        
        return dot
    
    def generate_svg(self, uml_diagram: UMLDiagram) -> str:
        """Generate SVG from the UML diagram"""
        try:
            dot = self.generate(uml_diagram)
            return dot.pipe().decode('utf-8')
        except Exception as e:
            # Return an error message as SVG
            error_dot = graphviz.Digraph(format='svg')
            error_dot.attr('graph', fontname='Arial')
            error_dot.node('error', f'Error generating diagram: {str(e)}', shape='box', style='filled', fillcolor='#ffcccc')
            return error_dot.pipe().decode('utf-8')
    
    def generate_base64_image(self, uml_diagram: UMLDiagram) -> str:
        """Generate base64 encoded image for embedding in HTML"""
        try:
            dot = self.generate(uml_diagram)
            svg_bytes = dot.pipe()
            return base64.b64encode(svg_bytes).decode('utf-8')
        except Exception as e:
            # Return an error message image
            error_dot = graphviz.Digraph(format='svg')
            error_dot.attr('graph', fontname='Arial')
            error_dot.node('error', f'Error generating diagram: {str(e)}', shape='box', style='filled', fillcolor='#ffcccc')
            svg_bytes = error_dot.pipe()
            return base64.b64encode(svg_bytes).decode('utf-8')
    
    def generate_png_bytes(self, uml_diagram: UMLDiagram) -> bytes:
        """Generate PNG bytes for download"""
        try:
            dot = self.generate(uml_diagram)
            dot.format = 'png'
            return dot.pipe()
        except Exception as e:
            # Return an error message image
            error_dot = graphviz.Digraph(format='png')
            error_dot.attr('graph', fontname='Arial')
            error_dot.node('error', f'Error generating diagram: {str(e)}', shape='box', style='filled', fillcolor='#ffcccc')
            return error_dot.pipe()
            
    def generate_package_diagram(self, uml_diagram: UMLDiagram) -> graphviz.Digraph:
        """Generate a package diagram showing relationships between packages"""
        dot = graphviz.Digraph(engine='dot', format='svg')
        dot.attr('graph', fontname='Arial', rankdir='TB')
        dot.attr('node', shape='folder', style='filled', fillcolor='lightyellow', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
        # Track packages and their classes
        packages = {}
        default_package = "Default"
        
        # Group classes by package
        for class_def in uml_diagram.classes:
            package_name = class_def.package if class_def.package else default_package
            if package_name not in packages:
                packages[package_name] = []
            packages[package_name].append(class_def.name)
            
        # Create package nodes
        for package_name, class_list in packages.items():
            # Create a label with the package name and class list
            class_text = "\\n".join(class_list)
            label = f"{package_name}\\n\\n{class_text}"
            dot.node(package_name, label=label)
            
        # Create edges between packages based on relationships
        package_dependencies = set()  # Track (source_package, target_package) pairs
        
        for rel in uml_diagram.relationships:
            source_class = rel.source
            target_class = rel.target
            
            # Find the packages for source and target classes
            source_package = default_package
            target_package = default_package
            
            for class_def in uml_diagram.classes:
                if class_def.name == source_class:
                    source_package = class_def.package if class_def.package else default_package
                if class_def.name == target_class:
                    target_package = class_def.package if class_def.package else default_package
                    
            # Only add edges between different packages
            if source_package != target_package:
                package_dependencies.add((source_package, target_package))
                
        # Add the edges to the graph
        for source_package, target_package in package_dependencies:
            dot.edge(source_package, target_package, style='dashed')
            
        return dot
        
    def generate_package_svg(self, uml_diagram: UMLDiagram) -> str:
        """Generate SVG for package diagram"""
        try:
            dot = self.generate_package_diagram(uml_diagram)
            return dot.pipe().decode('utf-8')
        except Exception as e:
            # Return an error message as SVG
            error_dot = graphviz.Digraph(format='svg')
            error_dot.attr('graph', fontname='Arial')
            error_dot.node('error', f'Error generating package diagram: {str(e)}', 
                         shape='box', style='filled', fillcolor='#ffcccc')
            return error_dot.pipe().decode('utf-8')
            
    def generate_package_png_bytes(self, uml_diagram: UMLDiagram) -> bytes:
        """Generate PNG bytes for package diagram download"""
        try:
            dot = self.generate_package_diagram(uml_diagram)
            dot.format = 'png'
            return dot.pipe()
        except Exception as e:
            # Return an error message image
            error_dot = graphviz.Digraph(format='png')
            error_dot.attr('graph', fontname='Arial')
            error_dot.node('error', f'Error generating package diagram: {str(e)}', 
                         shape='box', style='filled', fillcolor='#ffcccc')
            return error_dot.pipe()