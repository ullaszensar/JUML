# JUML User Guide

This guide provides detailed instructions on how to use JUML to generate UML class diagrams from your Java code.

## Getting Started

1. **Access the JUML application** through your web browser
2. **Prepare your Java code** by organizing your `.java` files and compressing them into a ZIP file
3. **Upload the ZIP file** to JUML using the file uploader on the main page
4. **Select folders to include** in your diagram to focus on specific parts of your codebase

## Understanding the Interface

JUML provides four main views for analyzing your code:

### 1. Class Diagram

The Class Diagram view shows all classes in your code with their attributes, methods, and relationships.

Features:
- **Filter by Package**: Use the dropdown to focus on classes in a specific package
- **Download Options**: Save the diagram as SVG (vector) or PNG (image) format
- **Zoom and Pan**: Use your browser's zoom functions to navigate large diagrams

Diagram Elements:
- **Classes**: Rectangular boxes with three compartments (name, attributes, methods)
- **Attributes**: Listed with visibility indicators (+, -, #), name, and type
- **Methods**: Listed with visibility indicators, name, parameters, and return type
- **Relationships**: Lines connecting classes showing their relationships

### 2. Package Diagram

The Package Diagram view shows dependencies between packages in your code.

Features:
- **Package Dependencies**: Visualize which packages depend on others
- **Package Contents**: See which classes belong to each package
- **Download Options**: Save the diagram as SVG or PNG

### 3. Hierarchy Explorer

The Hierarchy Explorer provides an interactive way to explore class inheritance hierarchies.

Features:
- **Root Classes**: Classes that don't inherit from other classes are shown as tabs
- **Class Details**: Each class shows its type (Class, Abstract Class, or Interface) and package
- **Tabbed Information**: Attributes, methods, and children are organized in tabs
- **Child Navigation**: Click on child classes to explore deeper into the hierarchy
- **Package Filtering**: Filter the hierarchy to focus on classes in a specific package

### 4. Data Analysis

The Data Analysis section provides additional insights into your code structure and potential sensitive data.

#### Demographic Data Analysis
This tab scans your Java code for fields that might store demographic or personal information.

Features:
- **Automated Detection**: Identifies fields related to personal data like names, addresses, gender, etc.
- **File-level Reports**: Shows which files contain potential sensitive data fields
- **Occurrence Counting**: Reports how frequently each field appears in the code
- **Tabular Display**: Each file's data is presented in a clear, organized table

#### Class Hierarchy Table
This tab presents class relationships in a searchable, tabular format.

Features:
- **Comprehensive View**: Shows all relationships between classes in your codebase
- **Search Functionality**: Find specific classes and their relationships
- **Relationship Types**: Displays inheritance, association, dependency, etc.
- **CSV Export**: Download the complete hierarchy table for offline analysis
- **Package Information**: See which package each class belongs to

## Working with UML Diagrams

### Understanding Relationships

JUML displays different types of relationships between classes:

- **Inheritance**: A solid line with a hollow triangle pointing to the parent class
- **Implementation**: A dashed line with a hollow triangle pointing to the interface
- **Association**: A solid line showing a general relationship between classes
- **Dependency**: A dashed line showing that one class depends on another
- **Aggregation**: A solid line with an empty diamond showing a "has-a" relationship
- **Composition**: A solid line with a filled diamond showing a "contains" relationship

### Tips for Better Diagrams

1. **Organize code into packages**: JUML works best when your code is organized into logical packages
2. **Include complete class hierarchies**: Include both parent and child classes for accurate inheritance visualization
3. **Use folder selection**: When uploading a ZIP file, select specific folders to include only relevant parts of your codebase
4. **Use package filtering**: For large codebases, use the package filter to focus on specific areas
5. **Hierarchy Explorer for inheritance**: Use the Hierarchy Explorer to understand inheritance relationships more clearly
6. **Download SVG for editing**: SVG format allows further editing in vector graphics software

### Using Folder Selection

The folder selection feature helps you manage large codebases by letting you focus on specific parts:

1. **Upload your ZIP file** containing Java code
2. **Review the available folders** extracted from your ZIP file
3. **Select the folders** you want to include in your diagram analysis
   - You can select multiple folders
   - JUML will only process Java files from the selected folders
   - Sub-folders of selected folders are automatically included
4. **Click "Generate Diagram"** to process only the selected folders

## Troubleshooting

### Common Issues

- **No classes shown**: Ensure your ZIP file contains `.java` files and they have proper class definitions
- **Missing relationships**: Check that both classes involved in a relationship are included in your code
- **Large diagrams**: For very large codebases, use package filtering to create more manageable views
- **Parsing errors**: Ensure your Java code compiles correctly, as syntax errors may affect parsing

### Getting Help

If you encounter issues not covered in this guide, please:
1. Check the README.md file for additional information
2. Check DEPLOYMENT.md for technical deployment issues
3. Report issues on the project's GitHub repository