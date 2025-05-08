import streamlit as st
import io
import base64
import json
import zipfile
import os
import tempfile
from typing import Dict, List, Any, Optional

from utils.parser import get_parser, ManualInputParser
from utils.uml_generator import UMLGenerator
from utils.data_models import ClassDefinition, Attribute, Method, Relationship, UMLDiagram
from utils.test_uml import generate_test_uml

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
    
    JUML makes it easy to generate UML class diagrams from your code:
    
    ### Simple 2-Step Process
    
    1. **Upload a ZIP file** containing your Java code files
       - The application will automatically extract all `.java` files
       - All extracted code is combined and analyzed together
    
    2. **Choose your diagram type**
       - **Class Diagram**: Traditional UML class diagram showing all classes and relationships
       - **Package Diagram**: Shows relationships between packages in your code
       - **Hierarchy Explorer**: Interactive explorer for class hierarchies with details on hover
    
    3. **View and download your diagram**
       - Class and Package diagrams can be downloaded in SVG or PNG format
       - Use the package filter dropdown to focus on specific packages
    
    ### UML Notation
    - Visibility: `+` (public), `-` (private), `#` (protected)
    - Relationships:
      - Inheritance: child class inherits from parent class
      - Implementation: class implements an interface
      - Association: general relationship between classes
      - Dependency: one class depends on another
      - Aggregation: "has-a" relationship (weak ownership)
      - Composition: "contains" relationship (strong ownership)
    
    ### Interactive Hierarchy Explorer
    - Expand and collapse classes to explore inheritance relationships
    - View detailed class information including attributes and methods
    - Filter by package to focus on specific parts of your codebase
    """)


def get_download_link(diagram: UMLDiagram, file_format: str, diagram_type: str = "class", selected_package: Optional[str] = None):
    """Generate a download link for the diagram
    
    Args:
        diagram: UML diagram data
        file_format: 'svg' or 'png'
        diagram_type: 'class' or 'package'
        selected_package: Optional package name to filter by
    """
    if diagram_type == "package":
        if file_format == 'svg':
            svg_content = generator.generate_package_svg(diagram)
            b64 = base64.b64encode(svg_content.encode()).decode()
            href = f'data:image/svg+xml;base64,{b64}'
            return href, 'svg'
        else:  # PNG
            png_bytes = generator.generate_package_png_bytes(diagram)
            b64 = base64.b64encode(png_bytes).decode()
            href = f'data:image/png;base64,{b64}'
            return href, 'png'
    else:  # Class diagram (default)
        if file_format == 'svg':
            svg_content = generator.generate_svg(diagram, selected_package)
            b64 = base64.b64encode(svg_content.encode()).decode()
            href = f'data:image/svg+xml;base64,{b64}'
            return href, 'svg'
        else:  # PNG
            png_bytes = generator.generate_png_bytes(diagram, selected_package)
            b64 = base64.b64encode(png_bytes).decode()
            href = f'data:image/png;base64,{b64}'
            return href, 'png'
        
def process_zip_file(uploaded_zip, language: str):
    """Process a zip file containing code files"""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write zip content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            temp_zip.write(uploaded_zip.getbuffer())
            temp_zip_path = temp_zip.name
        
        # Extract the zip file
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Remove the temporary zip file
        os.unlink(temp_zip_path)
        
        # Find all files with the appropriate extension based on language
        extensions = {
            "Python": [".py"],
            "Java": [".java"],
            "JavaScript": [".js"]
        }
        
        # Get appropriate extensions for selected language
        file_extensions = extensions.get(language, [])
        
        # Initialize an empty string to store all code
        all_code = ""
        
        # Walk through the directory and get all relevant files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                # Check if the file has a matching extension
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    # Read the file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            code = f.read()
                            # Add file content to combined code with a header comment
                            all_code += f"\n\n# File: {os.path.relpath(file_path, temp_dir)}\n{code}"
                        except Exception as e:
                            st.warning(f"Could not read file {file}: {str(e)}")
        
        return all_code


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


def create_hierarchy_explorer(uml_diagram: UMLDiagram, selected_package: Optional[str] = None):
    """Create an interactive class hierarchy explorer
    
    This component shows inheritance relationships between classes with hover effects
    for viewing class details.
    
    Args:
        uml_diagram: The UML diagram to visualize
        selected_package: Optional package name to filter by
    """
    if not uml_diagram.classes:
        st.info("No classes to display in the hierarchy explorer.")
        return
    
    # Filter classes by package if selected
    classes_to_display = uml_diagram.classes
    if selected_package and selected_package != "All Packages":
        classes_to_display = [cls for cls in uml_diagram.classes if cls.package == selected_package]
    
    # Find all inheritance relationships
    inheritance_relations = [rel for rel in uml_diagram.relationships 
                             if rel.type in ["inheritance", "implementation"]]
    
    # Build a hierarchy map: parent -> [children]
    hierarchy_map = {}
    for rel in inheritance_relations:
        child = rel.source
        parent = rel.target
        
        if parent not in hierarchy_map:
            hierarchy_map[parent] = []
        hierarchy_map[parent].append(child)
    
    # Find all classes that are children
    all_children = set()
    for children in hierarchy_map.values():
        all_children.update(children)
    
    # Find all available class names
    all_classes = {cls.name for cls in classes_to_display}
    
    # Find root classes (those that don't inherit from others)
    root_classes = all_classes - all_children
    
    # Add classes that have no displayed parents as roots
    for class_name in all_classes:
        if class_name in all_children:
            # Check if this class's parent is in the displayed classes
            parent_found = False
            for rel in inheritance_relations:
                if rel.source == class_name and rel.target in all_classes:
                    parent_found = True
                    break
            
            if not parent_found:
                root_classes.add(class_name)
    
    # Display instructions for the hierarchy explorer
    st.markdown("""
    ### Interactive Class Hierarchy Explorer
    
    Click on class names to view details. Classes are arranged by inheritance relationships.
    """)
    
    # Create a tab for each root class
    if root_classes:
        tabs = st.tabs([f"📌 {root}" for root in sorted(root_classes)])
        
        for i, root in enumerate(sorted(root_classes)):
            with tabs[i]:
                display_class_details(root, classes_to_display, hierarchy_map, all_classes)
    else:
        st.info("No root classes found in the diagram.")


def display_class_details(class_name: str, classes: List[ClassDefinition], 
                         hierarchy_map: Dict[str, List[str]], all_class_names: set):
    """Display details for a class and its children
    
    Args:
        class_name: Name of the class to display
        classes: List of all class definitions
        hierarchy_map: Map of parent classes to their children
        all_class_names: Set of all class names in the current view
    """
    # Find class definition
    class_def = next((cls for cls in classes if cls.name == class_name), None)
    if not class_def:
        st.warning(f"Class definition for '{class_name}' not found.")
        return
    
    # Create a visual container for the class
    with st.container():
        # Class header with styled box
        st.markdown(f"""
        <div style="border: 2px solid #4CAF50; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
            <h3 style="margin-top: 0;">{class_name}</h3>
            <p><strong>Type:</strong> {"Interface" if class_def.is_interface else "Abstract Class" if class_def.is_abstract else "Class"}</p>
            {f'<p><strong>Package:</strong> {class_def.package}</p>' if class_def.package else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for attributes, methods, and children
        class_tabs = st.tabs(["Attributes", "Methods", "Children"])
        
        # Attributes tab
        with class_tabs[0]:
            if class_def.attributes:
                for attr in class_def.attributes:
                    visibility_text = {"+" : "public", "-" : "private", "#" : "protected"}[attr.visibility]
                    static_text = "static " if attr.is_static else ""
                    st.markdown(f"""
                    <div style="margin-bottom: 5px; padding: 5px; background-color: #f9f9f9; border-left: 3px solid #2196F3;">
                        <span style="color: #666;">{visibility_text}</span> {static_text}<strong>{attr.name}</strong>: <span style="color: #007ACC;">{attr.type}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No attributes defined for this class.")
        
        # Methods tab
        with class_tabs[1]:
            if class_def.methods:
                for method in class_def.methods:
                    visibility_text = {"+" : "public", "-" : "private", "#" : "protected"}[method.visibility]
                    abstract_text = "abstract " if method.is_abstract else ""
                    static_text = "static " if method.is_static else ""
                    
                    # Format parameters
                    params = ", ".join([f"{p['name']}: {p['type']}" for p in method.parameters])
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 8px; padding: 5px; background-color: #f9f9f9; border-left: 3px solid #FFA000;">
                        <span style="color: #666;">{visibility_text}</span> {abstract_text}{static_text}<strong>{method.name}</strong>({params}): <span style="color: #007ACC;">{method.return_type}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No methods defined for this class.")
        
        # Children tab - show all classes that inherit from this one
        with class_tabs[2]:
            if class_name in hierarchy_map and hierarchy_map[class_name]:
                children = [child for child in hierarchy_map[class_name] if child in all_class_names]
                if children:
                    child_cols = st.columns(min(3, len(children)))
                    for i, child in enumerate(sorted(children)):
                        with child_cols[i % 3]:
                            # Find the child class definition
                            child_class = next((cls for cls in classes if cls.name == child), None)
                            if child_class:
                                class_type = "Interface" if child_class.is_interface else "Abstract" if child_class.is_abstract else "Class"
                                if st.button(f"{child} ({class_type})", key=f"child_{class_name}_{child}"):
                                    # Show details for the selected child class
                                    st.markdown("---")
                                    st.markdown(f"### Child: {child}")
                                    display_class_details(child, classes, hierarchy_map, all_class_names)
                else:
                    st.info("No children classes in the current view.")
            else:
                st.info("No children classes inherit from this class.")


def main():
    """Main function to run the Streamlit app"""
    st.title("JUML - UML Class Diagram Generator")
    
    # Sidebar for navigation
    sidebar_option = st.sidebar.radio(
        "Navigation",
        ["Generate Diagram", "Test Diagram", "Help"]
    )
    
    if sidebar_option == "Help":
        display_help()
        return
        
    if sidebar_option == "Test Diagram":
        st.info("This is a test page to verify diagram generation with simple test data.")
        generate_test_uml()
        return
    
    # Initialize session state for the UML diagram
    if 'uml_diagram' not in st.session_state:
        st.session_state.uml_diagram = UMLDiagram(classes=[], relationships=[])
    
    # Fixed to Java language only
    language = "Java"
    st.info("JUML is configured to parse Java code files (.java)")
    
    # Direct ZIP file upload interface
    st.write("Upload a ZIP file containing your code files")
    uploaded_file = st.file_uploader("Choose a ZIP file", type="zip")
    
    # Automatic diagram generation when file is uploaded
    if uploaded_file is not None:
        # Process the uploaded ZIP file
        with st.spinner(f"Processing ZIP file: {uploaded_file.name}..."):
            try:
                code = process_zip_file(uploaded_file, language)
                if code:
                    # Preview of extracted code
                    with st.expander("Preview of extracted code"):
                        preview_length = min(1000, len(code))
                        st.code(code[:preview_length] + ("..." if len(code) > preview_length else ""))
                    
                    # Automatically generate diagram
                    try:
                        parser = get_parser(language)
                        if parser:
                            uml_diagram = parser.parse(code)
                            st.session_state.uml_diagram = uml_diagram
                            st.success(f"Successfully parsed {language} code and generated diagram!")
                        else:
                            st.error(f"Parser for {language} not available.")
                    except Exception as e:
                        st.error(f"Error parsing code: {str(e)}")
                else:
                    st.warning(f"No {language} files found in the ZIP file.")
            except Exception as e:
                st.error(f"Error processing ZIP file: {str(e)}")
    
    # Display diagram section
    st.header("UML Class Diagram")
    
    if st.session_state.uml_diagram and st.session_state.uml_diagram.classes:
        # Display diagram info
        class_count = len(st.session_state.uml_diagram.classes)
        relationship_count = len(st.session_state.uml_diagram.relationships)
        st.info(f"Diagram contains {class_count} classes and {relationship_count} relationships")
        
        # Display diagram
        try:
            # Validate diagram data before generating
            if not st.session_state.uml_diagram.classes:
                st.warning("The diagram doesn't contain any classes. Make sure the uploaded ZIP file has valid Java code.")
                return
                
            # Select diagram type
            diagram_type = st.radio("Diagram Type", ["Class Diagram", "Package Diagram", "Hierarchy Explorer"], horizontal=True)
            
            # Generate diagram with enhanced error handling
            try:
                if diagram_type == "Class Diagram":
                    st.subheader("Class Diagram")
                    
                    # Get list of packages to filter by
                    packages = ["All Packages"]
                    for cls in st.session_state.uml_diagram.classes:
                        if cls.package and cls.package not in packages:
                            packages.append(cls.package)
                    
                    # Package filter dropdown
                    selected_package = st.selectbox("Filter by Package", packages, key="package_filter")
                    
                    # Apply package filter or show all classes
                    if selected_package == "All Packages":
                        svg_content = generator.generate_svg(st.session_state.uml_diagram)
                    else:
                        svg_content = generator.generate_svg(st.session_state.uml_diagram, selected_package)
                    
                    st.markdown(f'<div style="overflow: auto;">{svg_content}</div>', unsafe_allow_html=True)
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    with col1:
                        download_format = st.selectbox("Download Format", ["SVG", "PNG"], key="class_download_format")
                    
                    with col2:
                        # Pass selected package to download link generation
                        if selected_package == "All Packages":
                            href, ext = get_download_link(st.session_state.uml_diagram, download_format.lower(), "class")
                        else:
                            href, ext = get_download_link(st.session_state.uml_diagram, download_format.lower(), "class", selected_package)
                            
                        st.markdown(
                            f'<a href="{href}" download="class_diagram.{ext}"><button style="padding: 0.5em 1em; '
                            f'background-color: #4CAF50; color: white; border: none; '
                            f'border-radius: 4px; cursor: pointer;">Download Class Diagram</button></a>',
                            unsafe_allow_html=True
                        )
                elif diagram_type == "Package Diagram":
                    st.subheader("Package Diagram")
                    svg_content = generator.generate_package_svg(st.session_state.uml_diagram)
                    st.markdown(f'<div style="overflow: auto;">{svg_content}</div>', unsafe_allow_html=True)
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    with col1:
                        download_format = st.selectbox("Download Format", ["SVG", "PNG"], key="package_download_format")
                    
                    with col2:
                        href, ext = get_download_link(st.session_state.uml_diagram, download_format.lower(), "package")
                        st.markdown(
                            f'<a href="{href}" download="package_diagram.{ext}"><button style="padding: 0.5em 1em; '
                            f'background-color: #4CAF50; color: white; border: none; '
                            f'border-radius: 4px; cursor: pointer;">Download Package Diagram</button></a>',
                            unsafe_allow_html=True
                        )
                else:  # Hierarchy Explorer
                    st.subheader("Interactive Class Hierarchy Explorer")
                    
                    # Get list of packages to filter by
                    packages = ["All Packages"]
                    for cls in st.session_state.uml_diagram.classes:
                        if cls.package and cls.package not in packages:
                            packages.append(cls.package)
                    
                    # Package filter dropdown
                    selected_package = st.selectbox("Filter by Package", packages, key="hierarchy_package_filter")
                    
                    # Apply the package filter to the hierarchy explorer
                    create_hierarchy_explorer(st.session_state.uml_diagram, selected_package)
                
                # Clear diagram button
                if st.button("Clear Diagram"):
                    st.session_state.uml_diagram = UMLDiagram(classes=[], relationships=[])
                    st.session_state.classes = []
                    st.session_state.current_relationships = []
                    st.rerun()
            except Exception as e:
                st.error(f"Error rendering diagram: {str(e)}")
                st.info("Try uploading a different ZIP file with Java code.")
                
        except Exception as e:
            st.error(f"Error generating diagram: {str(e)}")
            st.info("There might be an issue with the diagram generation. Please try uploading a different Java code ZIP file.")
    else:
        st.info("No diagram to display. Please upload a ZIP file to generate a diagram.")


if __name__ == "__main__":
    main()
