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

#### Analysis Summary
This tab provides an overview of all key metrics and findings in your codebase.

Features:
- **Key Metrics**: Shows total classes, relationships, and demographic data fields
- **Class Structure Summary**: Displays distribution of classes across packages
- **Java File Summary**: Complete file-by-file breakdown of each source file's purpose and contents
  - Shows what each file does (Controller, Service, Entity, etc.)
  - Counts classes, interfaces and methods in each file
  - Indicates whether a file contains demographic data
  - Lists all demographic fields found in each file
- **Demographic Data Summary**: Consolidated table of all demographic fields found across all files
- **Relationship Type Summary**: Statistical breakdown of relationship types in your code
- **CSV Export**: Download any of the summary tables for offline analysis

#### Demographic Summary
This tab provides a dedicated summary focused only on files containing demographic data.

Features:
- **Focused View**: Shows only files containing demographic or personal information
- **File Type Classification**: Identifies what each file does (Controller, Service, Entity, etc.)
- **Summary Text**: Provides a concise summary of what demographic data each file contains
- **Field Details**: Shows both field names and their detected demographic categories
- **File Type Statistics**: Displays a breakdown of which types of files contain demographic data
- **CSV Export**: Download the complete demographic files summary for compliance review

#### Class Hierarchy Table
This tab presents class relationships in a searchable, tabular format.

Features:
- **Comprehensive View**: Shows all relationships between classes in your codebase
- **Search Functionality**: Find specific classes and their relationships
- **Relationship Types**: Displays inheritance, association, dependency, etc.
- **CSV Export**: Download the complete hierarchy table for offline analysis
- **Package Information**: See which package each class belongs to

#### Code Analysis
This tab provides comprehensive code analysis to identify quality, security, and performance issues.

Features:
- **Folder Selection**: Analyze all folders or select specific folders to focus on
- **Code Smell Detection**: Identifies issues like long methods, excessive parameters, magic numbers, etc.
- **Security Analysis**: Detects potential security vulnerabilities like SQL injection and hardcoded credentials
- **Performance Issue Detection**: Identifies inefficient code patterns that may impact performance
- **Design Pattern Recognition**: Detects common design patterns like Singleton, Factory, Observer, etc.
- **Complexity Metrics**: Measures cyclomatic and cognitive complexity of your code
- **CSV Export**: Download analysis results for offline review

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