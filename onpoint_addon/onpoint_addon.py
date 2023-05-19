bl_info = {
    "name": "On-Point Add-On",
    "author": "Trevor Smale",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > On-Point",
    "description": "Origin, Cursor, Axis and Parenting Tools",
    "warning": "",
    "wiki_url": "https://github.com/TrevorSmale/OnPoint/wiki",
    "category": "Object",
    "license": "MIT",
    "support": "Official"
}

import bpy

# Operator to reset the 3D cursor
class ResetCursorOperator(bpy.types.Operator):
    bl_idname = "view3d.reset_3d_cursor"
    bl_label = "Reset 3D Cursor"

    def execute(self, context):
        context.scene.cursor.location = (0.0, 0.0, 0.0)
        return {'FINISHED'}

# Operator to reset the 3D cursor rotation
class ResetCursorRotationOperator(bpy.types.Operator):
    bl_idname = "view3d.reset_3d_cursor_rotation"
    bl_label = "Reset 3D Cursor Rotation"

    def execute(self, context):
        context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        return {'FINISHED'}

# Operator to set the origin to world center
class OriginToWorldOperator(bpy.types.Operator):
    bl_idname = "object.origin_to_world"
    bl_label = "Origin to World Center"

    def execute(self, context):
        for obj in context.selected_objects:
            context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            bpy.ops.object.location_clear()
            obj.location = (0, 0, 0)
        return {'FINISHED'}

# Operator to snap 3D cursor to selected with zero rotation
class SnapCursorToSelectedOperator(bpy.types.Operator):
    bl_idname = "view3d.snap_cursor_to_selected_zero_rotation"
    bl_label = "Snap Cursor to Selected with Zero Rotation"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_selected()
        context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        return {'FINISHED'}

# Operator to place the parent axis
class PlaceParentAxisOperator(bpy.types.Operator):
    bl_idname = "object.place_parent_axis"
    bl_label = "Place Parent Axis"
    bl_description = "Place an empty plain axis at world 0,0,0 named 0_Parent_Axis in the Axis collection"

    def execute(self, context):
        collection_name = "Axis"
        object_name = "0_Parent_Axis"

        # Check if Axis collection exists, create if necessary
        if collection_name not in bpy.data.collections:
            bpy.data.collections.new(collection_name)

        # Check if object already exists
        if object_name in bpy.data.objects:
            self.report({'INFO'}, "Already placed")
            return {'CANCELLED'}

        # Create the object
        obj = bpy.data.objects.new(object_name, None)
        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = 1.0
        bpy.context.scene.collection.objects.link(obj)

        # Add the object to the Axis collection
        collection = bpy.data.collections.get(collection_name)
        collection.objects.link(obj)

        return {'FINISHED'}

# Operator to place the child axis
class PlaceChildAxisOperator(bpy.types.Operator):
    bl_idname = "object.place_child_axis"
    bl_label = "Place Child Axis"
    bl_description = "Place an empty plain axis at world 0,0,0 with Euler Rotation of 0,0,0 named '1_Child_Axis' within the Axis collection"

    def execute(self, context):
        collection_name = "Axis"
        parent_object_name = "0_Parent_Axis"
        child_object_base_name = "1_Child_Axis"
        max_child_axis_count = 10
        scale_factor = 0.5
        distance_x = 1.0

        # Check if Axis collection exists, create if necessary
        if collection_name not in bpy.data.collections:
            bpy.data.collections.new(collection_name)

        # Check if parent object exists
        if parent_object_name not in bpy.data.objects:
            self.report({'ERROR'}, "Must place Parent Axis first")
            return {'CANCELLED'}

        # Check if maximum child axis count reached
        child_axis_count = sum(1 for obj in bpy.data.objects if obj.name.startswith(child_object_base_name))
        if child_axis_count >= max_child_axis_count:
            self.report({'ERROR'}, "Maximum Child Axis count reached")
            return {'CANCELLED'}

        # Create the object
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        obj = bpy.context.object
        obj.name = f"{child_object_base_name}_{child_axis_count + 1}"

        # Set parent-child relationship
        parent_object = bpy.data.objects.get(parent_object_name)
        obj.parent = parent_object

        # Set scale of child axis
        obj.scale = [scale_factor, scale_factor, scale_factor]

        # Calculate X position based on child axis count
        x_position = distance_x * (child_axis_count + 1)

        # Place child axis at X+ position from world origin
        obj.location.x = x_position

        # Add the object to the Axis collection
        collection = bpy.data.collections.get(collection_name)
        collection.objects.link(obj)

        return {'FINISHED'}

# Operator to parent all meshes to the parent axis
class ParentAllMeshesOperator(bpy.types.Operator):
    bl_idname = "object.parent_all_meshes"
    bl_label = "Parent all Meshes to Parent Axis"
    bl_description = "Parent all mesh objects in the scene to the 0_Parent_Axis within the Axis collection"

    def execute(self, context):
        parent_object_name = "0_Parent_Axis"

        # Check if parent object exists
        if parent_object_name not in bpy.data.objects:
            self.report({'ERROR'}, "Parent Axis not found")
            return {'CANCELLED'}

        # Get all mesh objects in the scene
        mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

        if not mesh_objects:
            self.report({'ERROR'}, "No mesh objects found")
            return {'CANCELLED'}

        # Parent all mesh objects to the parent axis
        parent_object = bpy.data.objects.get(parent_object_name)
        for obj in mesh_objects:
            obj.parent = parent_object

        return {'FINISHED'}

# Operator to clear all parents of all objects while maintaining child axis parenting
class ClearAllParentsOperator(bpy.types.Operator):
    bl_idname = "object.clear_all_parents"
    bl_label = "Clear All Parents"
    bl_description = "Clear the parenting of all objects in the scene except for child axes"

    def execute(self, context):
        child_axis_prefix = "1_Child_Axis"

        # Clear parent of all objects except child axes
        for obj in bpy.data.objects:
            if obj.name.startswith(child_axis_prefix):
                continue
            obj.parent = None

        return {'FINISHED'}

# Operator to parent to object
class ParentToObjectOperator(bpy.types.Operator):
    bl_idname = "object.parent_to_object"
    bl_label = "Parent to Object"
    bl_description = "Parent selected objects to an active object"

    def execute(self, context):
        active_object = context.active_object
        selected_objects = context.selected_objects

        if not active_object:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        if not selected_objects:
            self.report({'ERROR'}, "No selected objects")
            return {'CANCELLED'}

        for obj in selected_objects:
            if obj != active_object:
                obj.parent = active_object

        return {'FINISHED'}

# Define the panel class
class OriginalPanel(bpy.types.Panel):
    bl_label = "On-Point"
    bl_idname = "OBJECT_PT_on_point_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "On-Point"

    def draw(self, context):
        layout = self.layout

        # Origin Tools
        row = layout.row()
        row.label(text="Origin Tools:")
        grid = layout.grid_flow(row_major=True, columns=1)

        for i in range(3):
            if i == 0:
                icon = "CLIPUV_HLT"
                text = "Origin to Geometry"
                grid.operator("object.origin_set", text=text, icon=icon).type = 'ORIGIN_GEOMETRY'

            elif i == 1:
                icon = "TRANSFORM_ORIGINS"
                text = "Origin to World"
                grid.operator(OriginToWorldOperator.bl_idname, text=text, icon=icon)

            elif i == 2:
                icon = "PIVOT_CURSOR"
                text = "Origin to Cursor"
                grid.operator("object.origin_set", text=text, icon=icon).type = 'ORIGIN_CURSOR'

        # Cursor Tools
        row = layout.row()
        row.label(text="Cursor Tools:")
        grid = layout.grid_flow(row_major=True, columns=1)

        for i in range(3):
            if i == 0:
                icon = "ORIENTATION_CURSOR"
                text = "Cursor to Selection"
                grid.operator(SnapCursorToSelectedOperator.bl_idname, text=text, icon=icon)

            elif i == 1:
                icon = "CURSOR"
                text = "Reset 3D Cursor"
                grid.operator(ResetCursorOperator.bl_idname, text=text, icon=icon)

            elif i == 2:
                icon = "PIVOT_CURSOR"
                text = "Zero Cursor Rotation"
                grid.operator(ResetCursorRotationOperator.bl_idname, text=text, icon=icon)

        # Axis Tools
        row = layout.row()
        row.label(text="Axis Tools:")
        grid = layout.grid_flow(row_major=True, columns=1)
        grid.operator(PlaceParentAxisOperator.bl_idname, text="Place Parent Axis", icon="OBJECT_ORIGIN")
        grid.operator(PlaceChildAxisOperator.bl_idname, text="Place Child Axis", icon="OBJECT_ORIGIN")

        # Parent Tools
        layout.label(text="Parent Tools:")
        layout.operator(ParentAllMeshesOperator.bl_idname, text="Meshes to Parent Axis", icon="FORCE_LENNARDJONES")
        layout.operator(ClearAllParentsOperator.bl_idname, text="Clear All Mesh Parents", icon="X")
        layout.operator(ParentToObjectOperator.bl_idname, text="Parent to Object", icon="CONSTRAINT")

        # Support
        layout.label(text="Support:")
        row = layout.row()
        row.operator("wm.url_open", text="Documentation", icon="FILE_BLANK").url = "https://github.com/trevorsmale/onpoint"
        row.operator("wm.url_open", text="Tip the Dev", icon="HEART").url = "https://ko-fi.com/trevorsmale"
        row = layout.row()
        row.operator("wm.url_open", text="Wiki", icon="INFO").url = bl_info["wiki_url"]

def register():
    bpy.utils.register_class(OriginalPanel)
    bpy.utils.register_class(ResetCursorOperator)
    bpy.utils.register_class(ResetCursorRotationOperator)
    bpy.utils.register_class(OriginToWorldOperator)
    bpy.utils.register_class(SnapCursorToSelectedOperator)
    bpy.utils.register_class(PlaceParentAxisOperator)
    bpy.utils.register_class(PlaceChildAxisOperator)
    bpy.utils.register_class(ParentAllMeshesOperator)
    bpy.utils.register_class(ClearAllParentsOperator)
    bpy.utils.register_class(ParentToObjectOperator)

def unregister():
    bpy.utils.unregister_class(OriginalPanel)
    bpy.utils.unregister_class(ResetCursorOperator)
    bpy.utils.unregister_class(ResetCursorRotationOperator)
    bpy.utils.unregister_class(OriginToWorldOperator)
    bpy.utils.unregister_class(SnapCursorToSelectedOperator)
    bpy.utils.unregister_class(PlaceParentAxisOperator)
    bpy.utils.unregister_class(PlaceChildAxisOperator)
    bpy.utils.unregister_class(ParentAllMeshesOperator)
    bpy.utils.unregister_class(ClearAllParentsOperator)
    bpy.utils.unregister_class(ParentToObjectOperator)

if __name__ == "__main__":
    register()
