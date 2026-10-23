"""Headless Blender render of original cat art; does not save/change the blend."""
import bpy,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from icon_pixels import read_png,write_png,padded_icon
source=ROOT/'art/EwingsCat_Adult.blend';out=ROOT/'release/icon-renders';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
scene.render.film_transparent=True;scene.view_settings.exposure=0.8
for obj in scene.objects:
    if obj.type=='ARMATURE':
        for bone in obj.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    if obj.name=='Preview ground':obj.hide_render=True
    if obj.type=='LIGHT':obj.data.energy*=2
cam=scene.camera;cam.data.type='ORTHO';cam.data.ortho_scale=.62
for name,location,target in [('Adult',(.65,.85,.44),(0,.04,.16)),('Kitten',(-.30,.95,.42),(0,.07,.16))]:
    cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    raw=out/(name+'.png');scene.render.filepath=str(raw);bpy.ops.render.render(write_still=True)
    path=ROOT/'stage/EwingsAnimals/42/media/textures'/('Item_EwingsCat_'+name+'.png')
    write_png(path,padded_icon(read_png(raw)));print('ORIGINAL_ICON_RENDERED',name)
