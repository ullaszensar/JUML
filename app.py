import streamlit as st
import io
import base64
import json
from typing import Dict, List, Any

from utils.parser import get_parser, ManualInputParser
from utils.uml_generator import UMLGenerator
from utils.data_models import ClassDefinition, Attribute, Method, Relationship, UMLDiagram

# Set page title and configure layout
st.set_page_config(
    page_title="JUML - UML Class Diagram Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the generator
generator = UMLGenerator()


def display_help():
    st.markdown("""
    ## How to use JUML
    
    JUML provides two ways to generate UML class diagrams:
    
    ### 1. Code Input
    - Select a programming language (Python, Java, or JavaScript)
    - Paste your code in the text area
    - Click "Generate Diagram" to parse the code and create a diagram
    
    ### 2. Manual Input
    - Add classes manually by providing:
      - Class name
      - Attributes (name, type, visibility)
      - Methods (name, parameters, return type, visibility)
    - Add relationships between classes
    - Edit classes and relationships as needed
    
    ### Sample JSON Format
    For manual input, you can also directly edit the JSON. Here's the format:
    
    ```json
    {
      "classes": [
        {
          "name": "MyClass",
          "attributes": [
            {
              "name": "attribute1",
              "type": "String",
              "visibility": "+",
              "is_static": false
            }
          ],
          "methods": [
            {
              "name": "myMethod",
              "return_type": "void",
              "parameters": [
                {
                  "name": "param1",
                  "type": "int"
                }
              ],
              "visibility": "+",
              "is_static": false,
              "is_abstract": false
            }
          ],
          "is_abstract": false,
          "is_interface": false
        }
      ],
      "relationships": [
        {
          "source": "ChildClass",
          "target": "ParentClass",
          "type": "inheritance",
          "label": "",
          "multiplicity": ""
        }
      ]
    }
    ```
    
    ### UML Notation
    - Visibility: `+` (public), `-` (private), `#` (protected)
    - Relationships:
      - Inheritance: child class inherits from parent class
      - Implementation: class implements an interface
      - Association: general relationship between classes
      - Dependency: one class depends on another
      - Aggregation: "has-a" relationship (weak ownership)
      - Composition: "contains" relationship (strong ownership)
    """)


def get_download_link(diagram: UMLDiagram, file_format: str):
    """Generate a download link for the diagram"""
    if file_format == 'svg':
        svg_content = generator.generate_svg(diagram)
        b64 = base64.b64encode(svg_content.encode()).decode()
        href = f'data:image/svg+xml;base64,{b64}'
        return href, 'svg'
    else:  # PNG
        png_bytes = generator.generate_png_bytes(diagram)
        b64 = base64.b64encode(png_bytes).decode()
        href = f'data:image/png;base64,{b64}'
        return href, 'png'


def create_class_editor():
    """Create UI for defining a class"""
    col1, col2 = st.columns(2)
    
    with col1:
        class_name = st.text_input("Class Name", key="class_name")
        is_abstract = st.checkbox("Abstract Class", key="is_abstract")
        is_interface = st.checkbox("Interface", key="is_interface")
    
    with col2:
        package = st.text_input("Package", key="package")
    
    st.subheader("Attributes")
    
    attributes = []
    
    # Get attributes from session state
    if "current_attributes" not in st.session_state:
        st.session_state.current_attributes = []
    
    # Display existing attributes
    for i, attr in enumerate(st.session_state.current_attributes):
        cols = st.columns([3, 2, 1, 1, 1])
        with cols[0]:
            attr["name"] = st.text_input("Name", attr["name"], key=f"attr_name_{i}")
        with cols[1]:
            attr["type"] = st.text_input("Type", attr["type"], key=f"attr_type_{i}")
        with cols[2]:
            attr["visibility"] = st.selectbox(
                "Visibility", 
                ["+", "-", "#"], 
                ["+", "-", "#"].index(attr["visibility"]),
                key=f"attr_vis_{i}"
            )
        with cols[3]:
            attr["is_static"] = st.checkbox("Static", attr["is_static"], key=f"attr_static_{i}")
        with cols[4]:
            if st.button("Delete", key=f"delete_attr_{i}"):
                st.session_state.current_attributes.pop(i)
                st.rerun()
    
    # Add new attribute
    if st.button("Add Attribute"):
        st.session_state.current_attributes.append({
            "name": "",
            "type": "",
            "visibility": "+",
            "is_static": False
        })
        st.rerun()
    
    st.subheader("Methods")
    
    methods = []
    
    # Get methods from session state
    if "current_methods" not in st.session_state:
        st.session_state.current_methods = []
    
    # Display existing methods
    for i, method in enumerate(st.session_state.current_methods):
        st.markdown(f"**Method {i+1}**")
        cols1 = st.columns([3, 2, 2, 1, 1])
        
        with cols1[0]:
            method["name"] = st.text_input("Name", method["name"], key=f"method_name_{i}")
        with cols1[1]:
            method["return_type"] = st.text_input("Return Type", method["return_type"], key=f"method_return_{i}")
        with cols1[2]:
            method["visibility"] = st.selectbox(
                "Visibility", 
                ["+", "-", "#"], 
                ["+", "-", "#"].index(method["visibility"]),
                key=f"method_vis_{i}"
            )
        with cols1[3]:
            method["is_static"] = st.checkbox("Static", method["is_static"], key=f"method_static_{i}")
        with cols1[4]:
            method["is_abstract"] = st.checkbox("Abstract", method["is_abstract"], key=f"method_abstract_{i}")
        
        # Get parameters from session state
        if f"params_{i}" not in st.session_state:
            st.session_state[f"params_{i}"] = method.get("parameters", [])
        
        st.markdown("**Parameters**")
        for j, param in enumerate(st.session_state[f"params_{i}"]):
            param_cols = st.columns([3, 2, 1])
            with param_cols[0]:
                param["name"] = st.text_input("Param Name", param["name"], key=f"param_name_{i}_{j}")
            with param_cols[1]:
                param["type"] = st.text_input("Param Type", param["type"], key=f"param_type_{i}_{j}")
            with param_cols[2]:
                if st.button("Delete Param", key=f"delete_param_{i}_{j}"):
                    st.session_state[f"params_{i}"].pop(j)
                    st.rerun()
        
        method["parameters"] = st.session_state[f"params_{i}"]
        
        cols2 = st.columns([1, 1])
        with cols2[0]:
            if st.button("Add Parameter", key=f"add_param_{i}"):
                st.session_state[f"params_{i}"].append({"name": "", "type": ""})
                st.rerun()
        with cols2[1]:
            if st.button("Delete Method", key=f"delete_method_{i}"):
                st.session_state.current_methods.pop(i)
                # Also remove params
                if f"params_{i}" in st.session_state:
                    del st.session_state[f"params_{i}"]
                st.rerun()
        
        st.markdown("---")
    
    # Add new method
    if st.button("Add Method"):
        st.session_state.current_methods.append({
            "name": "",
            "return_type": "",
            "parameters": [],
            "visibility": "+",
            "is_static": False,
            "is_abstract": False
        })
        st.rerun()
    
    # Extract data from form values
    if class_name:
        # Convert attributes to Attribute objects
        attr_objects = []
        for attr in st.session_state.current_attributes:
            attr_objects.append(
                Attribute(
                    name=attr["name"],
                    type=attr["type"],
                    visibility=attr["visibility"],
                    is_static=attr["is_static"]
                )
            )
        
        # Convert methods to Method objects
        method_objects = []
        for i, method in enumerate(st.session_state.current_methods):
            method_objects.append(
                Method(
                    name=method["name"],
                    return_type=method["return_type"],
                    parameters=method["parameters"],
                    visibility=method["visibility"],
                    is_static=method["is_static"],
                    is_abstract=method["is_abstract"]
                )
            )
        
        return ClassDefinition(
            name=class_name,
            attributes=attr_objects,
            methods=method_objects,
            is_abstract=is_abstract,
            is_interface=is_interface,
            package=package
        )
    
    return None


def create_relationship_editor(class_names: List[str]):
    """Create UI for defining relationships between classes"""
    st.subheader("Relationships")
    
    if "current_relationships" not in st.session_state:
        st.session_state.current_relationships = []
    
    # Display existing relationships
    for i, rel in enumerate(st.session_state.current_relationships):
        cols = st.columns([2, 2, 2, 2, 2, 1])
        
        with cols[0]:
            rel["source"] = st.selectbox("Source", class_names, 
                                         class_names.index(rel["source"]) if rel["source"] in class_names else 0,
                                         key=f"rel_source_{i}")
        
        with cols[1]:
            rel["type"] = st.selectbox(
                "Type", 
                ["inheritance", "implementation", "association", "dependency", "aggregation", "composition"],
                ["inheritance", "implementation", "association", "dependency", "aggregation", "composition"].index(rel["type"]),
                key=f"rel_type_{i}"
            )
        
        with cols[2]:
            rel["target"] = st.selectbox("Target", class_names, 
                                         class_names.index(rel["target"]) if rel["target"] in class_names else 0,
                                         key=f"rel_target_{i}")
        
        with cols[3]:
            rel["label"] = st.text_input("Label", rel["label"], key=f"rel_label_{i}")
        
        with cols[4]:
            rel["multiplicity"] = st.text_input("Multiplicity", rel["multiplicity"], key=f"rel_mult_{i}")
            
        with cols[5]:
            if st.button("Delete", key=f"delete_rel_{i}"):
                st.session_state.current_relationships.pop(i)
                st.rerun()
    
    # Add new relationship if there are at least 2 classes
    if len(class_names) >= 2:
        if st.button("Add Relationship"):
            st.session_state.current_relationships.append({
                "source": class_names[0],
                "target": class_names[1],
                "type": "association",
                "label": "",
                "multiplicity": ""
            })
            st.rerun()
    else:
        st.info("Add at least two classes to create relationships")
    
    # Extract relationship objects
    relationships = []
    for rel in st.session_state.current_relationships:
        relationships.append(
            Relationship(
                source=rel["source"],
                target=rel["target"],
                type=rel["type"],
                label=rel["label"],
                multiplicity=rel["multiplicity"]
            )
        )
    
    return relationships


def main():
    """Main function to run the Streamlit app"""
    st.title("JUML - UML Class Diagram Generator")
    
    # Sidebar for navigation
    sidebar_option = st.sidebar.radio(
        "Navigation",
        ["Generate Diagram", "Help"]
    )
    
    if sidebar_option == "Help":
        display_help()
        return
    
    # Initialize session state for the UML diagram
    if 'uml_diagram' not in st.session_state:
        st.session_state.uml_diagram = UMLDiagram(classes=[], relationships=[])
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["Code Input", "Manual Input", "View Diagram"])
    
    with tab1:
        st.header("Generate UML from Code")
        
        # Language selection
        language = st.selectbox(
            "Select programming language",
            ["Python", "Java", "JavaScript"]
        )
        
        # Code input
        code = st.text_area("Paste your code here", height=300)
        
        # Parse button
        if st.button("Generate Diagram"):
            if code:
                try:
                    parser = get_parser(language)
                    if parser:
                        uml_diagram = parser.parse(code)
                        st.session_state.uml_diagram = uml_diagram
                        st.success(f"Successfully parsed {language} code!")
                        
                        # Automatically switch to the View Diagram tab
                        st.rerun()
                    else:
                        st.error(f"Parser for {language} not available.")
                except Exception as e:
                    st.error(f"Error parsing code: {str(e)}")
            else:
                st.error("Please enter some code to parse.")
    
    with tab2:
        st.header("Manual UML Definition")
        
        tab2a, tab2b = st.tabs(["Form Input", "JSON Editor"])
        
        with tab2a:
            # Initialize class list in session state
            if 'classes' not in st.session_state:
                st.session_state.classes = []
            
            # Create new class section
            st.subheader("Create New Class")
            
            # Handle class editor
            new_class = create_class_editor()
            
            if st.button("Add Class to Diagram"):
                if new_class:
                    # Add the class to the session state list
                    st.session_state.classes.append(new_class)
                    
                    # Clear the form
                    st.session_state.current_attributes = []
                    st.session_state.current_methods = []
                    
                    st.success(f"Added class {new_class.name} to the diagram!")
                    st.rerun()
                else:
                    st.error("Please enter a class name.")
            
            # Display existing classes and allow editing
            if st.session_state.classes:
                st.subheader("Existing Classes")
                
                class_names = [cls.name for cls in st.session_state.classes]
                
                for i, cls in enumerate(st.session_state.classes):
                    with st.expander(f"{cls.name}"):
                        st.json(cls.to_dict())
                        
                        if st.button(f"Delete {cls.name}", key=f"delete_class_{i}"):
                            # Remove the class
                            st.session_state.classes.pop(i)
                            
                            # Remove any relationships involving this class
                            if "current_relationships" in st.session_state:
                                st.session_state.current_relationships = [
                                    rel for rel in st.session_state.current_relationships
                                    if rel["source"] != cls.name and rel["target"] != cls.name
                                ]
                            
                            st.success(f"Deleted class {cls.name}")
                            st.rerun()
                
                # Relationship editor
                st.markdown("---")
                relationships = create_relationship_editor(class_names)
                
                # Generate diagram button
                if st.button("Generate Diagram from Manual Input"):
                    uml_diagram = UMLDiagram(
                        classes=st.session_state.classes,
                        relationships=relationships
                    )
                    st.session_state.uml_diagram = uml_diagram
                    st.success("UML diagram updated!")
                    st.rerun()
        
        with tab2b:
            st.subheader("JSON Editor")
            
            # Convert current diagram to JSON
            if st.session_state.uml_diagram:
                json_data = {
                    "classes": [cls.model_dump() for cls in st.session_state.uml_diagram.classes],
                    "relationships": [rel.model_dump() for rel in st.session_state.uml_diagram.relationships]
                }
                initial_json = json.dumps(json_data, indent=2)
            else:
                # Provide a sample structure
                initial_json = json.dumps({
                    "classes": [],
                    "relationships": []
                }, indent=2)
            
            # JSON editor
            json_input = st.text_area("Edit JSON directly", initial_json, height=400)
            
            if st.button("Parse JSON"):
                try:
                    parser = ManualInputParser()
                    uml_diagram = parser.parse(json_input)
                    
                    # Update both the UML diagram and the class list
                    st.session_state.uml_diagram = uml_diagram
                    st.session_state.classes = uml_diagram.classes
                    
                    # Update relationships
                    st.session_state.current_relationships = [
                        {
                            "source": rel.source,
                            "target": rel.target,
                            "type": rel.type,
                            "label": rel.label,
                            "multiplicity": rel.multiplicity
                        }
                        for rel in uml_diagram.relationships
                    ]
                    
                    st.success("Successfully parsed JSON input!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error parsing JSON: {str(e)}")
    
    with tab3:
        st.header("UML Class Diagram")
        
        if st.session_state.uml_diagram and st.session_state.uml_diagram.classes:
            # Display diagram info
            class_count = len(st.session_state.uml_diagram.classes)
            relationship_count = len(st.session_state.uml_diagram.relationships)
            st.info(f"Diagram contains {class_count} classes and {relationship_count} relationships")
            
            # Display diagram
            try:
                svg_content = generator.generate_svg(st.session_state.uml_diagram)
                st.markdown(f'<div style="overflow: auto;">{svg_content}</div>', unsafe_allow_html=True)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    download_format = st.selectbox("Download Format", ["SVG", "PNG"])
                
                with col2:
                    href, ext = get_download_link(st.session_state.uml_diagram, download_format.lower())
                    st.markdown(
                        f'<a href="{href}" download="uml_diagram.{ext}"><button style="padding: 0.5em 1em; '
                        f'background-color: #4CAF50; color: white; border: none; '
                        f'border-radius: 4px; cursor: pointer;">Download {download_format}</button></a>',
                        unsafe_allow_html=True
                    )
                
                # Clear diagram button
                if st.button("Clear Diagram"):
                    st.session_state.uml_diagram = UMLDiagram(classes=[], relationships=[])
                    st.session_state.classes = []
                    st.session_state.current_relationships = []
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error generating diagram: {str(e)}")
        else:
            st.info("No diagram to display. Please generate a diagram from code or create one manually.")


if __name__ == "__main__":
    main()
