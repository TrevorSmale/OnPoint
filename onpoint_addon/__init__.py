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

# Import your scripts here
from . import operators

classes = [
    operators.ResetCursorOperator,
    operators.ResetCursorRotationOperator,
    operators.OriginToWorldOperator,
    operators.SnapCursorToSelectedOperator,
    operators.PlaceParentAxisOperator,
    operators.PlaceChildAxisOperator,
    operators.ParentAllMeshesOperator,
    operators.ClearAllParentsOperator,
    operators.ParentToObjectOperator,
    operators.OriginalPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
