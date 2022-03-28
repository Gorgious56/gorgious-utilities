import bpy
from collections import defaultdict
from gorgious_utilities.collection.helper import get_collection_layers_from_collections, get_family_down


def copy_struct(source, target):
    if not source or not target:
        return
    for name, prop in source.bl_rna.properties.items():
        if name == "rna_type":
            continue
        try:
            setattr(target, name, getattr(source, name))
        except AttributeError:
            new_source = getattr(source, name)
            new_target = getattr(target, name)
            if hasattr(new_source, "bl_rna"):
                copy_struct(new_source, new_target)
        except TypeError:
            pass

class GU_OT_clean_sort_view_layers(bpy.types.Operator):
    bl_idname = "clean.sort_view_layers"
    bl_label = "Sort View Layers"
    bl_options = {"UNDO"}

    def execute(self, context):
        active_view_layer_name = context.window.view_layer.name
        view_layers = context.scene.view_layers
        names_sorted = sorted((v_l.name for v_l in view_layers), key=lambda n: n.lower())
        l_c_mapping = defaultdict(dict)
        for view_layer in view_layers:
            layer_cols = set(
                get_collection_layers_from_collections(view_layer, list(get_family_down(context.scene.collection)))
            )
            for lc in layer_cols:
                l_c_mapping[view_layer.name][lc.name] = lc.exclude

        # context.scene.view_layers.new("__TEMPORARY_VIEW_LAYER__")  # Proxy that lets us remove all the other view layers
        for v_l in context.scene.view_layers:
            v_l.name = v_l.name + "__TEMPORARY_VIEW_LAYER__"
        # for v_l_name in names_sorted:
        #     context.scene.view_layers.remove(context.scene.view_layers[v_l_name])
        for v_l_name in names_sorted:
            new = context.scene.view_layers.new(v_l_name)
            context.window.view_layer = new
            states = l_c_mapping[v_l_name]
            layer_cols = get_collection_layers_from_collections(new, list(get_family_down(context.scene.collection)))
            for l_c in layer_cols:
                l_c.exclude = states[l_c.name]
        # context.scene.view_layers.remove(context.scene.view_layers["__TEMPORARY_VIEW_LAYER__"])
        for v_l_name in names_sorted:
            context.scene.view_layers.remove(context.scene.view_layers[v_l_name])
        context.window.view_layer = context.scene.view_layers[active_view_layer_name]
        return {"FINISHED"}


if __name__ == "__main__":
    bpy.utils.register_class(GU_OT_clean_sort_view_layers)
