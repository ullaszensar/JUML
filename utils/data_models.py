from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Attribute(BaseModel):
    """Model for a class attribute"""
    name: str
    type: str = ""
    visibility: str = "+" # +: public, -: private, #: protected
    is_static: bool = False


class Method(BaseModel):
    """Model for a class method"""
    name: str
    return_type: str = ""
    parameters: List[Dict[str, str]] = []
    visibility: str = "+" # +: public, -: private, #: protected
    is_static: bool = False
    is_abstract: bool = False


class Relationship(BaseModel):
    """Model for relationships between classes"""
    source: str
    target: str
    type: str  # inheritance, association, dependency, aggregation, composition
    label: str = ""
    multiplicity: str = ""


class ClassDefinition(BaseModel):
    """Model for a class definition"""
    name: str
    attributes: List[Attribute] = []
    methods: List[Method] = []
    is_abstract: bool = False
    is_interface: bool = False
    package: Optional[str] = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "attributes": [attr.model_dump() for attr in self.attributes],
            "methods": [method.model_dump() for method in self.methods],
            "is_abstract": self.is_abstract,
            "is_interface": self.is_interface,
            "package": self.package
        }


class UMLDiagram(BaseModel):
    """Model for the complete UML diagram"""
    classes: List[ClassDefinition] = []
    relationships: List[Relationship] = []
