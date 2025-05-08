# JUML - Java UML Class Diagram Generator

JUML is a web-based application that automatically generates UML class diagrams from Java source code. It provides an intuitive interface for visualizing class structures, relationships, and hierarchies to help developers better understand and document their Java projects.

## Features

- **Java Code Parsing**: Automatically extracts class definitions, methods, attributes, and relationships from Java code
- **UML Class Diagram Generation**: Visualizes classes with their attributes and methods in standard UML notation
- **Package Diagram**: Shows relationships between packages in your codebase
- **Interactive Class Hierarchy Explorer**: Navigate through class inheritance hierarchies with detailed information
- **Package Filtering**: Filter diagrams to focus on specific packages
- **Export Options**: Download diagrams as SVG or PNG files

## Deployment

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/juml.git
   cd juml
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install the required packages**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   streamlit run app.py
   ```

5. **Access the application**:
   Open your browser and go to `http://localhost:5000`

### Deploying on Replit

This project is optimized for deployment on Replit:

1. Fork this project on Replit
2. The `.streamlit/config.toml` file is already configured for proper deployment
3. Run the application by clicking the Run button
4. Share your application using the provided Replit URL

## How to Use

### Generating a UML Diagram

1. **Prepare your Java code**:
   - Zip your Java source files into a single ZIP archive
   - Make sure your ZIP contains `.java` files (optionally organized in directories)

2. **Upload the ZIP file**:
   - Click the "Choose a ZIP file" button in the application
   - Select your ZIP file containing Java code
   - The application will automatically extract and analyze your code

3. **View the diagram**:
   - Once processed, the UML diagram will be displayed
   - Use the "Diagram Type" radio buttons to switch between:
     - Class Diagram: Shows all classes with attributes and methods
     - Package Diagram: Shows relationships between packages
     - Hierarchy Explorer: Interactive navigation of class hierarchies

4. **Filter by package**:
   - Use the "Filter by Package" dropdown to focus on specific packages
   - "All Packages" shows the complete diagram

5. **Download the diagram**:
   - Select your preferred format (SVG or PNG)
   - Click the "Download" button to save the diagram to your computer

### Understanding the Diagram

- **Classes** are represented as boxes with three sections:
  - Top: Class name
  - Middle: Attributes
  - Bottom: Methods

- **Visibility** is indicated by symbols:
  - `+` Public
  - `-` Private
  - `#` Protected

- **Relationships** are shown as lines between classes:
  - Inheritance: Solid line with hollow triangle
  - Implementation: Dashed line with hollow triangle
  - Association: Solid line
  - Dependency: Dashed line
  - Aggregation: Solid line with hollow diamond
  - Composition: Solid line with filled diamond

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Diagram generation powered by [Graphviz](https://graphviz.org/)