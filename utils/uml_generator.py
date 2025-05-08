import graphviz
import base64
import io
from typing import List, Dict, Any
import re

from utils.data_models import UMLDiagram, ClassDefinition, Relationship


class UMLGenerator:
    """Generate UML diagrams using Graphviz"""
    
    def __init__(self):
        """Initialize the UML generator"""
        pass
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters in text"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
    def _format_attributes(self, attributes: List[Dict[str, Any]]) -> List[str]:
        """Format attributes for display in the UML diagram"""
        formatted = []
        for attr in attributes:
            # Format: visibility name: type
            static_marker = "{static} " if attr.get('is_static', False) else ""
            name = self._escape_html(attr.get('name', ''))
            type_str = f": {self._escape_html(attr.get('type', ''))}" if attr.get('type') else ""
            formatted.append(f"{static_marker}{attr.get('visibility', '+')} {name}{type_str}")
        return formatted
    
    def _format_methods(self, methods: List[Dict[str, Any]]) -> List[str]:
        """Format methods for display in the UML diagram"""
        formatted = []
        for method in methods:
            # Format: visibility name(param1: type, param2: type): return_type
            static_marker = "{static} " if method.get('is_static', False) else ""
            abstract_marker = "{abstract} " if method.get('is_abstract', False) else ""
            
            # Format parameters
            params = []
            for param in method.get('parameters', []):
                param_name = self._escape_html(param.get('name', ''))
                param_type = f": {self._escape_html(param.get('type', ''))}" if param.get('type') else ""
                params.append(f"{param_name}{param_type}")
            
            name = self._escape_html(method.get('name', ''))
            param_str = ", ".join(params)
            return_type = f": {self._escape_html(method.get('return_type', ''))}" if method.get('return_type') else ""
            
            formatted.append(f"{static_marker}{abstract_marker}{method.get('visibility', '+')} {name}({param_str}){return_type}")
        
        return formatted
    
    def generate(self, uml_diagram: UMLDiagram) -> graphviz.Digraph:
        """Generate a Graphviz diagram from the UML model"""
        dot = graphviz.Digraph(engine='dot', format='svg')
        dot.attr('node', shape='record', style='filled', fillcolor='white')
        dot.attr('edge', fontsize='10')
        dot.attr(rankdir='TB')
        
        # Create nodes for classes
        for class_def in uml_diagram.classes:
            name = class_def.name
            
            # Prepare name with indicators for abstract/interface
            display_name = name
            if class_def.is_interface:
                display_name = f"«interface»\\n{name}"
            elif class_def.is_abstract:
                display_name = f"«abstract»\\n{name}"
            
            # Attribute part
            attributes = self._format_attributes([attr.model_dump() for attr in class_def.attributes])
            attr_text = "\\n".join(attributes) if attributes else " "
            
            # Method part
            methods = self._format_methods([method.model_dump() for method in class_def.methods])
            method_text = "\\n".join(methods) if methods else " "
            
            # Construct the label using proper Graphviz HTML-like label format
            # Class name section
            label = f"{{{display_name}|{attr_text}|{method_text}}}"
            
            dot.node(name, label=label)
        
        # Create edges for relationships
        for rel in uml_diagram.relationships:
            source = rel.source
            target = rel.target
            
            # Default styling
            edge_style = {
                'dir': 'none',
                'arrowhead': 'none',
                'arrowtail': 'none',
                'label': rel.label
            }
            
            # Set style based on relationship type
            if rel.type == "inheritance":
                edge_style['dir'] = 'back'
                edge_style['arrowtail'] = 'empty'
                edge_style['style'] = 'solid'
            elif rel.type == "implementation":
                edge_style['dir'] = 'back'
                edge_style['arrowtail'] = 'empty'
                edge_style['style'] = 'dashed'
            elif rel.type == "association":
                edge_style['dir'] = 'none'
                edge_style['style'] = 'solid'
            elif rel.type == "dependency":
                edge_style['dir'] = 'forward'
                edge_style['arrowhead'] = 'vee'
                edge_style['style'] = 'dashed'
            elif rel.type == "aggregation":
                edge_style['dir'] = 'back'
                edge_style['arrowtail'] = 'odiamond'
                edge_style['style'] = 'solid'
            elif rel.type == "composition":
                edge_style['dir'] = 'back'
                edge_style['arrowtail'] = 'diamond'
                edge_style['style'] = 'solid'
            
            # Add multiplicity if specified
            if rel.multiplicity:
                edge_style['label'] = rel.multiplicity if not rel.label else f"{rel.label}\n{rel.multiplicity}"
            
            dot.edge(source, target, **edge_style)
        
        return dot
    
    def generate_svg(self, uml_diagram: UMLDiagram) -> str:
        """Generate SVG from the UML diagram"""
        dot = self.generate(uml_diagram)
        return dot.pipe().decode('utf-8')
    
    def generate_base64_image(self, uml_diagram: UMLDiagram) -> str:
        """Generate base64 encoded image for embedding in HTML"""
        dot = self.generate(uml_diagram)
        svg_bytes = dot.pipe()
        return base64.b64encode(svg_bytes).decode('utf-8')
    
    def generate_png_bytes(self, uml_diagram: UMLDiagram) -> bytes:
        """Generate PNG bytes for download"""
        dot = self.generate(uml_diagram)
        # Change format to PNG
        dot.format = 'png'
        return dot.pipe()
