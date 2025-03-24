import bpy
import math
from mathutils import Vector

class HumanoidRig:
    """
    HumanoidRig - A Blender auto-rigging system for humanoid characters
    
    This class handles the creation and setup of a humanoid rig through
    an iterative process with visual feedback at each step.
    """
    
    def __init__(self):
        self.reference_points = {}
        self.armature_obj = None
        self.bones = {}
        self.step_completed = {
            "create_reference_points": False,
            "validate_reference_points": False,
            "create_armature": False,
            "adjust_bones": False,
            "weight_paint": False,
            "test_deformation": False
        }
    
    def create_reference_points(self):
        """Create reference points for key anatomical landmarks"""
        # Clear existing reference points
        for name in list(self.reference_points.keys()):
            if name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[name])
            self.reference_points.pop(name)
        
        # Define key anatomical positions
        positions = {
            "head": (0, 0, 1.7),
            "neck": (0, 0, 1.5),
            "spine_top": (0, 0, 1.3),
            "spine_mid": (0, 0, 1.0),
            "spine_bottom": (0, 0, 0.8),
            "left_shoulder": (-0.2, 0, 1.4),
            "right_shoulder": (0.2, 0, 1.4),
            "left_elbow": (-0.5, 0, 1.2),
            "right_elbow": (0.5, 0, 1.2),
            "left_wrist": (-0.7, 0, 1.0),
            "right_wrist": (0.7, 0, 1.0),
            "left_hip": (-0.1, 0, 0.8),
            "right_hip": (0.1, 0, 0.8),
            "left_knee": (-0.15, 0, 0.5),
            "right_knee": (0.15, 0, 0.5),
            "left_ankle": (-0.15, 0, 0.1),
            "right_ankle": (0.15, 0, 0.1),
            "left_toe": (-0.15, 0.1, 0),
            "right_toe": (0.15, 0.1, 0)
        }
        
        # Create empties as reference points
        for name, position in positions.items():
            bpy.ops.object.empty_add(type='SPHERE', radius=0.05, location=position)
            empty = bpy.context.active_object
            empty.name = f"ref_{name}"
            self.reference_points[name] = empty
        
        self.step_completed["create_reference_points"] = True
        return "Reference points created. Adjust them to match your character's anatomy."
    
    def validate_reference_points(self):
        """Validate that reference points are positioned logically"""
        if not self.step_completed["create_reference_points"]:
            return "Please create reference points first."
        
        # Check if all reference points exist
        for name in self.reference_points:
            if name not in self.reference_points or self.reference_points[name] is None:
                return f"Reference point '{name}' is missing."
        
        # Validate basic positioning (e.g., head above neck, shoulders at similar height)
        validation_checks = [
            (self.reference_points["head"].location.z > self.reference_points["neck"].location.z, 
             "Head should be above neck"),
            (self.reference_points["neck"].location.z > self.reference_points["spine_top"].location.z, 
             "Neck should be above spine_top"),
            (abs(self.reference_points["left_shoulder"].location.z - self.reference_points["right_shoulder"].location.z) < 0.1, 
             "Shoulders should be at similar heights"),
            (abs(self.reference_points["left_hip"].location.z - self.reference_points["right_hip"].location.z) < 0.1, 
             "Hips should be at similar heights")
        ]
        
        for check, message in validation_checks:
            if not check:
                return f"Validation failed: {message}"
        
        self.step_completed["validate_reference_points"] = True
        return "Reference points validated successfully."
    
    def create_armature(self):
        """Create the armature structure based on reference points"""
        if not self.step_completed["validate_reference_points"]:
            return "Please validate reference points first."
        
        # Create armature object
        bpy.ops.object.armature_add(location=(0, 0, 0))
        self.armature_obj = bpy.context.active_object
        self.armature_obj.name = "HumanoidRig"
        
        # Enter edit mode to add bones
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = self.armature_obj.data.edit_bones
        
        # Remove default bone
        for bone in edit_bones:
            edit_bones.remove(bone)
        
        # Create spine bones
        spine_points = ["spine_bottom", "spine_mid", "spine_top", "neck", "head"]
        prev_bone = None
        for i in range(len(spine_points) - 1):
            start_name = spine_points[i]
            end_name = spine_points[i+1]
            
            bone = edit_bones.new(start_name)
            bone.head = self.reference_points[start_name].location
            bone.tail = self.reference_points[end_name].location
            
            if prev_bone:
                bone.parent = prev_bone
            
            prev_bone = bone
            self.bones[start_name] = bone
        
        # Create limb bones
        limb_chains = [
            ["left_shoulder", "left_elbow", "left_wrist"],
            ["right_shoulder", "right_elbow", "right_wrist"],
            ["left_hip", "left_knee", "left_ankle", "left_toe"],
            ["right_hip", "right_knee", "right_ankle", "right_toe"]
        ]
        
        for chain in limb_chains:
            parent_bone = None
            
            # Determine parent bone for this chain
            if "shoulder" in chain[0]:
                parent_bone = self.bones["spine_top"]
            elif "hip" in chain[0]:
                parent_bone = self.bones["spine_bottom"]
            
            # Create bones in chain
            for i in range(len(chain) - 1):
                start_name = chain[i]
                end_name = chain[i+1]
                
                bone = edit_bones.new(start_name)
                bone.head = self.reference_points[start_name].location
                bone.tail = self.reference_points[end_name].location
                
                if i == 0 and parent_bone:
                    bone.parent = parent_bone
                elif i > 0:
                    bone.parent = self.bones[chain[i-1]]
                
                self.bones[start_name] = bone
        
        # Exit edit mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.step_completed["create_armature"] = True
        return "Armature created. Review bone placement and proceed to adjustment."
    
    def adjust_bones(self):
        """Adjust bone roll and other properties"""
        if not self.step_completed["create_armature"]:
            return "Please create the armature first."
        
        bpy.context.view_layer.objects.active = self.armature_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Calculate bone rolls
        # For arms and legs, calculate roll to align with body plane
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = self.armature_obj.data.edit_bones
        
        # Set bone roll for arms
        arm_bones = ["left_shoulder", "left_elbow", "right_shoulder", "right_elbow"]
        for bone_name in arm_bones:
            if bone_name in edit_bones:
                bone = edit_bones[bone_name]
                # Make Z-axis point forward
                bone.roll = 0 if "right" in bone_name else math.pi
        
        # Set bone roll for legs
        leg_bones = ["left_hip", "left_knee", "right_hip", "right_knee"]
        for bone_name in leg_bones:
            if bone_name in edit_bones:
                bone = edit_bones[bone_name]
                # Make Z-axis point forward
                bone.roll = 0 if "right" in bone_name else math.pi
        
        bpy.ops.object.mode_set(mode='POSE')
        
        # Add IK constraints for limbs
        pose_bones = self.armature_obj.pose.bones
        
        # Example: Add IK constraint for left arm
        if "left_elbow" in pose_bones:
            ik = pose_bones["left_elbow"].constraints.new('IK')
            ik.target = self.armature_obj
            if "left_wrist" in pose_bones:
                ik.subtarget = "left_wrist"
            ik.chain_count = 2
        
        # Example: Add IK constraint for right arm
        if "right_elbow" in pose_bones:
            ik = pose_bones["right_elbow"].constraints.new('IK')
            ik.target = self.armature_obj
            if "right_wrist" in pose_bones:
                ik.subtarget = "right_wrist"
            ik.chain_count = 2
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.step_completed["adjust_bones"] = True
        return "Bone adjustments completed. Ready for weight painting."
    
    def weight_paint(self, mesh_obj=None):
        """Apply automatic weight painting to a mesh"""
        if not self.step_completed["adjust_bones"]:
            return "Please adjust bones first."
        
        if mesh_obj is None:
            # Find a mesh in the scene to use
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and obj != self.armature_obj:
                    mesh_obj = obj
                    break
        
        if mesh_obj is None:
            return "No mesh found for weight painting. Please specify a mesh object."
        
        # Select the mesh and then the armature
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        self.armature_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.armature_obj
        
        # Parent mesh to armature with automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        
        self.step_completed["weight_paint"] = True
        return f"Automatic weight painting applied to {mesh_obj.name}."
    
    def test_deformation(self):
        """Test the rig by posing it"""
        if not self.step_completed["weight_paint"]:
            return "Please complete weight painting first."
        
        # Select armature
        bpy.ops.object.select_all(action='DESELECT')
        self.armature_obj.select_set(True)
        bpy.context.view_layer.objects.active = self.armature_obj
        
        # Enter pose mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # Set a simple test pose
        pose_bones = self.armature_obj.pose.bones
        
        if "left_shoulder" in pose_bones:
            pose_bones["left_shoulder"].rotation_euler.z = 0.5
        
        if "right_shoulder" in pose_bones:
            pose_bones["right_shoulder"].rotation_euler.z = -0.5
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.step_completed["test_deformation"] = True
        return "Test pose applied. Review deformation quality and make any necessary adjustments."
    
    def get_completion_status(self):
        """Return the current completion status of all steps"""
        return self.step_completed
    
    def reset(self):
        """Reset the rigging process"""
        # Remove armature if it exists
        if self.armature_obj and self.armature_obj.name in bpy.data.objects:
            bpy.data.objects.remove(self.armature_obj)
        
        # Remove reference points
        for name, obj in self.reference_points.items():
            if obj and obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj)
        
        # Reset variables
        self.reference_points = {}
        self.armature_obj = None
        self.bones = {}
        for step in self.step_completed:
            self.step_completed[step] = False
            
        return "Rigging process has been reset."

# Register an operator to create the rig
class OBJECT_OT_create_humanoid_rig(bpy.types.Operator):
    bl_idname = "object.create_humanoid_rig"
    bl_label = "Create Humanoid Rig"
    bl_description = "Create a humanoid rig with an iterative process"
    bl_options = {'REGISTER', 'UNDO'}
    
    step: bpy.props.EnumProperty(
        items=[
            ('create_reference_points', "Create Reference Points", "Create reference points"),
            ('validate_reference_points', "Validate Reference Points", "Validate reference points"),
            ('create_armature', "Create Armature", "Create the armature"),
            ('adjust_bones', "Adjust Bones", "Adjust bone properties"),
            ('weight_paint', "Weight Paint", "Apply automatic weight painting"),
            ('test_deformation', "Test Deformation", "Test the rig deformation"),
            ('reset', "Reset", "Reset the rigging process"),
        ],
        name="Step",
        description="Rigging step to perform",
        default='create_reference_points'
    )
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    def execute(self, context):
        # Get or create the rig instance
        if not hasattr(bpy.types.Scene, "humanoid_rig"):
            bpy.types.Scene.humanoid_rig = HumanoidRig()
        
        rig = bpy.types.Scene.humanoid_rig
        
        # Execute the selected step
        if self.step == 'create_reference_points':
            self.report({'INFO'}, rig.create_reference_points())
        elif self.step == 'validate_reference_points':
            self.report({'INFO'}, rig.validate_reference_points())
        elif self.step == 'create_armature':
            self.report({'INFO'}, rig.create_armature())
        elif self.step == 'adjust_bones':
            self.report({'INFO'}, rig.adjust_bones())
        elif self.step == 'weight_paint':
            # Get the active mesh object
            mesh_obj = None
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    mesh_obj = obj
                    break
            
            self.report({'INFO'}, rig.weight_paint(mesh_obj))
        elif self.step == 'test_deformation':
            self.report({'INFO'}, rig.test_deformation())
        elif self.step == 'reset':
            self.report({'INFO'}, rig.reset())
        
        return {'FINISHED'}

# Register a panel to display in the sidebar
class VIEW3D_PT_humanoid_rig(bpy.types.Panel):
    bl_label = "Humanoid Rig"
    bl_idname = "VIEW3D_PT_humanoid_rig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig'
    
    def draw(self, context):
        layout = self.layout
        
        # Get rig instance status
        if hasattr(bpy.types.Scene, "humanoid_rig"):
            rig = bpy.types.Scene.humanoid_rig
            status = rig.get_completion_status()
            
            # Display current status
            box = layout.box()
            box.label(text="Progress:")
            for step, completed in status.items():
                icon = 'CHECKMARK' if completed else 'X'
                box.label(text=f"{step.replace('_', ' ').title()}: {icon}")
        
        # Buttons for each step
        layout.label(text="Rigging Steps:")
        layout.operator("object.create_humanoid_rig", text="1. Create Reference Points").step = 'create_reference_points'
        layout.operator("object.create_humanoid_rig", text="2. Validate Reference Points").step = 'validate_reference_points'
        layout.operator("object.create_humanoid_rig", text="3. Create Armature").step = 'create_armature'
        layout.operator("object.create_humanoid_rig", text="4. Adjust Bones").step = 'adjust_bones'
        layout.operator("object.create_humanoid_rig", text="5. Weight Paint").step = 'weight_paint'
        layout.operator("object.create_humanoid_rig", text="6. Test Deformation").step = 'test_deformation'
        
        layout.separator()
        layout.operator("object.create_humanoid_rig", text="Reset Rigging Process").step = 'reset'

# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_create_humanoid_rig)
    bpy.utils.register_class(VIEW3D_PT_humanoid_rig)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_humanoid_rig)
    bpy.utils.unregister_class(OBJECT_OT_create_humanoid_rig)
    
    # Clean up the rig instance
    if hasattr(bpy.types.Scene, "humanoid_rig"):
        del bpy.types.Scene.humanoid_rig

if __name__ == "__main__":
    register() 