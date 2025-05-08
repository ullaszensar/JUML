import streamlit as st
from utils.data_models import UMLDiagram, ClassDefinition, Attribute, Method, Relationship
from utils.uml_generator import UMLGenerator

# Create a simple test UML diagram
def create_test_diagram():
    # Create some classes
    class1 = ClassDefinition(
        name="Person",
        attributes=[
            Attribute(name="name", type="String", visibility="+"),
            Attribute(name="age", type="int", visibility="+")
        ],
        methods=[
            Method(name="getName", return_type="String", visibility="+"),
            Method(name="setName", parameters=[{"name": "name", "type": "String"}], return_type="void", visibility="+")
        ]
    )
    
    class2 = ClassDefinition(
        name="Employee",
        attributes=[
            Attribute(name="employeeId", type="String", visibility="+"),
            Attribute(name="salary", type="double", visibility="-")
        ],
        methods=[
            Method(name="getSalary", return_type="double", visibility="+"),
            Method(name="setSalary", parameters=[{"name": "salary", "type": "double"}], return_type="void", visibility="+")
        ]
    )
    
    class3 = ClassDefinition(
        name="IPayable",
        is_interface=True,
        methods=[
            Method(name="calculatePay", return_type="double", visibility="+", is_abstract=True)
        ]
    )
    
    # Create relationships
    rel1 = Relationship(
        source="Employee",
        target="Person",
        type="inheritance"
    )
    
    rel2 = Relationship(
        source="Employee",
        target="IPayable",
        type="implementation"
    )
    
    # Create the diagram
    diagram = UMLDiagram(
        classes=[class1, class2, class3],
        relationships=[rel1, rel2]
    )
    
    return diagram

def generate_test_uml():
    # Create test diagram
    diagram = create_test_diagram()
    
    # Generate SVG
    generator = UMLGenerator()
    
    try:
        svg_content = generator.generate_svg(diagram)
        st.subheader("Test Diagram")
        st.markdown(f'<div style="overflow: auto;">{svg_content}</div>', unsafe_allow_html=True)
        st.success("Test diagram generated successfully!")
        return True
    except Exception as e:
        st.error(f"Error generating test diagram: {str(e)}")
        return False