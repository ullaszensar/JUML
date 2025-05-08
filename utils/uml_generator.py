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
    
    def _format_attributes(self, attributes: List[Dict[str, Any]]) -> List[str]:
        """Format attributes for display in the UML diagram"""
        formatted = []
        for attr in attributes:
            # Format: visibility name: type
            static_marker = "{static} " if attr.get('is_static', False) else ""
            type_str = f": {attr.get('type', '')}" if attr.get('type') else ""
            formatted.append(f"{static_marker}{attr.get('visibility', '+')} {attr.get('name', '')}{type_str}")
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
                param_type = f": {param.get('type')}" if param.get('type') else ""
                params.append(f"{param.get('name', '')}{param_type}")
            
            param_str = ", ".join(params)
            return_type = f": {method.get('return_type', '')}" if method.get('return_type') else ""
            
            formatted.append(f"{static_marker}{abstract_marker}{method.get('visibility', '+')} {method.get('name', '')}({param_str}){return_type}")
        
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
            
            # Title part - includes class name
            title = f"<B>{name}</B>"
            if class_def.is_interface:
                title = f"<B>«interface»<BR/>{name}</B>"
            elif class_def.is_abstract:
                title = f"<B>«abstract»<BR/>{name}</B>"
            
            # Attribute part
            attributes = self._format_attributes([attr.model_dump() for attr in class_def.attributes])
            attr_text = "<BR/>".join(attributes) if attributes else " "
            
            # Method part
            methods = self._format_methods([method.model_dump() for method in class_def.methods])
            method_text = "<BR/>".join(methods) if methods else " "
            
            # Construct the label
            label = f"{{{{<TR><TD>{title}</TD></TR>|<TR><TD ALIGN='LEFT'>{attr_text}</TD></TR>|<TR><TD ALIGN='LEFT'>{method_text}</TD></TR>}}}}"
            
            dot.node(name, label=f"<{label}>")
        
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
