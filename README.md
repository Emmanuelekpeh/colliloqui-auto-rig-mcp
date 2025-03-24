# Colliloqui Auto-Rig MCP

An iterative auto-rigging system for Blender, with a step-by-step approach that provides visual feedback at each stage of the rigging process.

## Features

- **Iterative Rigging Process**: Instead of a one-time execution, the rigging process is broken down into manageable steps
- **Visual Feedback**: Check and adjust at each stage before proceeding
- **Customizable Reference Points**: Position reference points to match your character's anatomy
- **Humanoid Rig**: Designed specifically for humanoid characters
- **Blender Integration**: Adds a dedicated panel to Blender's UI

## Installation

1. Download the repository
2. In Blender, go to Edit > Preferences > Add-ons > Install
3. Navigate to the downloaded `auto_rig_mcp.py` file and select it
4. Enable the add-on

## Usage

After installation, you'll find a new "Humanoid Rig" panel in the sidebar of the 3D viewport (press N to toggle the sidebar).

The rigging process consists of 6 steps:

1. **Create Reference Points**: Creates spheres that mark key anatomical positions
2. **Validate Reference Points**: Checks that the points are positioned logically
3. **Create Armature**: Builds the bone structure based on the reference points
4. **Adjust Bones**: Sets bone roll and adds IK constraints
5. **Weight Paint**: Applies automatic weight painting to your mesh
6. **Test Deformation**: Applies a test pose to check deformation quality

It's recommended to follow these steps in order, adjusting as needed at each stage.

## Custom Positioning

After creating reference points, you can manually reposition them to match your specific character's anatomy. The rig will be created based on these positions.

## Requirements

- Blender 2.80 or higher

## License

MIT License - Feel free to use and modify for your projects.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for bugs and feature requests. 