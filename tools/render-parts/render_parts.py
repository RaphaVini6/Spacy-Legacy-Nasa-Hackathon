"""
Builds a simple 3D model of every hardware part used in the simulator and renders it.

    blender -b -P tools/render-parts/render_parts.py -- <output dir> [part ids...]

Output: <id>.webp (transparent background) for each part in backend/Data/components.json.
"""
import math
import sys

import bpy
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = args[0] if args else "//renders"
ONLY = set(args[1:])

RES = (640, 480)
SAMPLES = 64


# ---------------------------------------------------------------- scene

def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = -0.35
    try:
        sc.render.image_settings.file_format = "WEBP"
        sc.render.image_settings.quality = 90
    except TypeError:
        sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"

    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.05, 0.06, 0.09, 1)
    bg.inputs[1].default_value = 0.6
    sc.world = world

    cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    cam.data.lens = 55
    sc.collection.objects.link(cam)
    sc.camera = cam

    def light(name, loc, energy, size, color):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.size, data.color = energy, size, color
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        obj.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(obj)

    light("key", (3.5, -3.5, 4.5), 900, 3.0, (1.0, 0.95, 0.88))
    light("rim", (-3.5, 3.5, 2.5), 700, 2.5, (0.65, 0.8, 1.0))
    light("fill", (-4.0, -2.5, 1.0), 220, 4.0, (1.0, 1.0, 1.0))
    return cam


def clear_parts():
    for o in list(bpy.data.objects):
        if o.type in {"MESH", "CURVE", "EMPTY"}:
            bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves):
        for d in list(coll):
            coll.remove(d)


# ---------------------------------------------------------------- materials

_mats = {}


def _set(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


def mat(name, color, metal=0.0, rough=0.5, emit=0.0, bump=None, coat=0.0):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    _set(p, ["Base Color"], (*color, 1))
    _set(p, ["Metallic"], metal)
    _set(p, ["Roughness"], rough)
    if coat:
        _set(p, ["Coat Weight", "Clearcoat"], coat)
    if emit:
        _set(p, ["Emission Color", "Emission"], (*color, 1))
        _set(p, ["Emission Strength"], emit)
    if bump:
        scale, strength = bump
        tex = nt.nodes.new("ShaderNodeTexNoise")
        _set(tex, ["Scale"], scale)
        _set(tex, ["Detail"], 6.0)
        b = nt.nodes.new("ShaderNodeBump")
        _set(b, ["Strength"], strength)
        nt.links.new(tex.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    _mats[name] = m
    return m


def materials():
    return dict(
        alu=mat("alu", (0.82, 0.83, 0.85), 1, 0.28),
        brushed=mat("brushed", (0.7, 0.71, 0.73), 1, 0.4, bump=(60, 0.05)),
        steel=mat("steel", (0.58, 0.59, 0.6), 1, 0.35),
        titanium=mat("titanium", (0.52, 0.48, 0.44), 1, 0.32),
        dark=mat("dark", (0.025, 0.025, 0.03), 0.3, 0.45),
        graphite=mat("graphite", (0.07, 0.07, 0.075), 0.7, 0.5),
        white=mat("white", (0.86, 0.86, 0.84), 0, 0.45),
        foil=mat("foil", (1.0, 0.68, 0.25), 1, 0.22, bump=(14, 0.55)),
        silverfoil=mat("silverfoil", (0.9, 0.9, 0.92), 1, 0.2, bump=(14, 0.5)),
        cell=mat("cell", (0.015, 0.03, 0.13), 0.3, 0.32),
        copper=mat("copper", (0.95, 0.52, 0.32), 1, 0.3),
        gold=mat("gold", (1.0, 0.77, 0.34), 1, 0.18),
        pcb=mat("pcb", (0.02, 0.22, 0.07), 0, 0.38, coat=0.4),
        pcbblue=mat("pcbblue", (0.02, 0.06, 0.2), 0, 0.38, coat=0.4),
        pcbblack=mat("pcbblack", (0.008, 0.03, 0.015), 0, 0.55),
        chip=mat("chip", (0.015, 0.015, 0.018), 0, 0.35),
        ceramic=mat("ceramic", (0.75, 0.72, 0.66), 0, 0.5),
        red=mat("red", (0.6, 0.04, 0.03), 0, 0.4),
        black=mat("black", (0.01, 0.01, 0.01), 0, 0.5),
        kapton=mat("kapton", (0.85, 0.32, 0.02), 0, 0.2, coat=0.6),
        green=mat("greenwrap", (0.05, 0.35, 0.12), 0, 0.3, coat=0.5),
        blue=mat("bluewrap", (0.03, 0.15, 0.55), 0, 0.3, coat=0.5),
        navy=mat("navy", (0.04, 0.07, 0.16), 0.2, 0.4),
        agc=mat("agc", (0.5, 0.42, 0.24), 0.75, 0.42),
        bluegray=mat("bluegray", (0.22, 0.27, 0.33), 0.3, 0.45),
        carbon=mat("carbon", (0.03, 0.03, 0.035), 0.2, 0.3, bump=(120, 0.15), coat=1.0),
        glow=mat("glow", (1.0, 0.35, 0.06), 0, 0.5, emit=8),
        led=mat("led", (0.2, 1.0, 0.35), 0, 0.5, emit=6),
        ledred=mat("ledred", (1.0, 0.1, 0.05), 0, 0.5, emit=6),
        display=mat("display", (0.25, 1.0, 0.4), 0, 0.5, emit=2.5),
        ice=mat("ice", (0.8, 0.9, 1.0), 0, 0.15),
    )


# ---------------------------------------------------------------- primitives

def _finish(o, m, smooth=False, bevel=0.0):
    if m is not None:
        o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments = bevel, 3
        mod.limit_method = "ANGLE"
    if smooth:
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
        except (AttributeError, RuntimeError):
            bpy.ops.object.shade_smooth()
    return o


def box(size, loc=(0, 0, 0), m=None, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.data.transform(Matrix.Diagonal((*size, 1)))
    return _finish(o, m, bevel=bevel)


def cyl(r, depth, loc=(0, 0, 0), m=None, rot=(0, 0, 0), verts=48, bevel=0.0, smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    return _finish(bpy.context.active_object, m, smooth, bevel)


def cone(r1, r2, depth, loc=(0, 0, 0), m=None, rot=(0, 0, 0), verts=48):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot, vertices=verts)
    return _finish(bpy.context.active_object, m, True)


def sphere(r, loc=(0, 0, 0), m=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    o = bpy.context.active_object
    o.data.transform(Matrix.Diagonal((*scale, 1)))
    return _finish(o, m, True)


def torus(major, minor, loc=(0, 0, 0), m=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=64, minor_segments=16)
    return _finish(bpy.context.active_object, m, True)


def rod(p1, p2, r, m):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
    return cyl(r, d.length, (p1 + p2) / 2, m, rot, verts=20)


def tube(points, r, m, closed=False):
    cu = bpy.data.curves.new("tube", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth, cu.bevel_resolution = r, 4
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for pt, co in zip(sp.points, points):
        pt.co = (*co, 1)
    sp.use_cyclic_u = closed
    o = bpy.data.objects.new("tube", cu)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    return o


def mesh_obj(name, verts, faces, m):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(m)
    me.shade_smooth()
    return o


def dish(radius, depth, loc, m, rot=(0, 0, 0), thickness=0.02):
    """Paraboloid reflector opening towards +z (before rotation)."""
    rings, seg = 14, 64
    verts = [(0, 0, 0)]
    for i in range(1, rings + 1):
        rr = radius * i / rings
        z = depth * (rr / radius) ** 2
        verts += [(rr * math.cos(2 * math.pi * k / seg), rr * math.sin(2 * math.pi * k / seg), z) for k in range(seg)]
    faces = [(0, 1 + k, 1 + (k + 1) % seg) for k in range(seg)]
    for i in range(rings - 1):
        a, b = 1 + i * seg, 1 + (i + 1) * seg
        faces += [(a + k, a + (k + 1) % seg, b + (k + 1) % seg, b + k) for k in range(seg)]
    o = mesh_obj("dish", verts, faces, m)
    o.location, o.rotation_euler = loc, rot
    s = o.modifiers.new("solid", "SOLIDIFY")
    s.thickness = thickness
    return o


def helix(radius, height, turns, phase=0.0, z0=0.0, steps=160):
    return [(radius * math.cos(phase + 2 * math.pi * turns * t / steps),
             radius * math.sin(phase + 2 * math.pi * turns * t / steps),
             z0 + height * t / steps) for t in range(steps + 1)]


# ---------------------------------------------------------------- parts

def p_no_power_source(M):
    cyl(0.5, 0.18, (0.9, 0, 0.5), M["dark"], (0, math.pi / 2, 0), bevel=0.01)
    torus(0.42, 0.025, (1.0, 0, 0.5), M["ledred"], (0, math.pi / 2, 0))
    for y in (-0.13, 0.13):
        cyl(0.05, 0.05, (0.99, y, 0.5), M["black"], (0, math.pi / 2, 0), verts=16)
    cyl(0.17, 0.45, (-0.15, 0.05, 0.22), M["dark"], (0, math.pi / 2, 0.2), bevel=0.01)
    for y in (-0.1, 0.1):
        rod((0.08, 0.05 + y + 0.04, 0.22), (0.32, 0.1 + y + 0.04, 0.22), 0.025, M["copper"])
    tube([(-0.37, 0.0, 0.22), (-0.6, -0.05, 0.12), (-0.85, 0.2, 0.06), (-1.1, 0.35, 0.06),
          (-1.4, 0.1, 0.06), (-1.6, -0.25, 0.06)], 0.06, M["black"])


def p_solar_panels(M):
    cyl(0.04, 0.55, (0, 0, 0.27), M["alu"])
    box((0.16, 0.16, 0.1), (0, 0, 0.58), M["alu"], bevel=0.01)
    for side in (-1, 1):
        cx = side * 0.92
        box((1.62, 1.04, 0.035), (cx, 0, 0.6), M["white"], bevel=0.005)
        for i in range(8):
            for j in range(5):
                x = cx - 0.7 + i * 0.2
                y = -0.4 + j * 0.2
                box((0.185, 0.185, 0.012), (x, y, 0.62), M["cell"])
        box((1.62, 0.03, 0.05), (cx, 0.53, 0.6), M["alu"])
        box((1.62, 0.03, 0.05), (cx, -0.53, 0.6), M["alu"])


def _rtg(M, r, h, fins, fin_len, fin_t, body, fin_m, caps):
    cyl(r, h, (0, 0, 0), body, bevel=0.01)
    for k in range(fins):
        a = 2 * math.pi * k / fins
        d = r + fin_len / 2 - 0.01
        box((fin_len, fin_t, h * 0.92), (d * math.cos(a), d * math.sin(a), 0), fin_m, (0, 0, a), bevel=0.004)
    for z in (h / 2, -h / 2):
        cyl(r * 1.08, 0.05, (0, 0, z), caps, bevel=0.01)


def p_rtg_snap19(M):
    _rtg(M, 0.22, 0.75, 6, 0.42, 0.03, M["graphite"], M["graphite"], M["steel"])
    cyl(0.1, 0.12, (0, 0, 0.45), M["steel"])


def p_rtg_snap27(M):
    _rtg(M, 0.2, 1.0, 8, 0.24, 0.025, M["brushed"], M["brushed"], M["brushed"])
    sphere(0.2, (0, 0, 0.52), M["brushed"], (1, 1, 0.45))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        rod((0.24 * math.cos(a), 0.24 * math.sin(a), -0.52), (0.4 * math.cos(a), 0.4 * math.sin(a), -0.75), 0.02, M["steel"])


def p_mmrtg(M):
    _rtg(M, 0.3, 0.7, 8, 0.32, 0.04, M["steel"], M["dark"], M["steel"])
    for z in (0.38, -0.38):
        cyl(0.18, 0.08, (0, 0, z), M["steel"])


def p_no_battery(M):
    box((1.2, 0.8, 0.04), (0, 0, 0.02), M["alu"], bevel=0.01)
    for x in (-0.6, 0.6):
        box((0.04, 0.8, 0.22), (x, 0, 0.13), M["alu"])
    for y in (-0.4, 0.4):
        box((1.2, 0.04, 0.22), (0, y, 0.13), M["alu"])
    for k in range(4):
        cyl(0.03, 0.06, (-0.45 + k * 0.3, 0, 0.06), M["steel"], verts=6)
    tube([(0.75, 0.25, 0.25), (0.95, 0.3, 0.2), (1.1, 0.5, 0.06), (1.35, 0.6, 0.06)], 0.035, M["red"])
    tube([(0.75, -0.2, 0.25), (0.95, -0.25, 0.2), (1.15, -0.4, 0.06), (1.4, -0.3, 0.06)], 0.035, M["black"])
    cyl(0.06, 0.08, (1.36, 0.6, 0.06), M["copper"], (0, math.pi / 2, 0))
    cyl(0.06, 0.08, (1.41, -0.3, 0.06), M["copper"], (0, math.pi / 2, 0))


def _cell_box(M, housing, caps):
    box((1.1, 0.7, 0.55), (0, 0, 0.275), housing, bevel=0.025)
    for i in range(4):
        for j in range(3):
            cyl(0.07, 0.04, (-0.39 + i * 0.26, -0.22 + j * 0.22, 0.56), caps, verts=24)
    cyl(0.05, 0.12, (-0.45, 0.42, 0.45), M["red"], (math.pi / 2, 0, 0))
    cyl(0.05, 0.12, (0.45, 0.42, 0.45), M["black"], (math.pi / 2, 0, 0))


def p_silver_zinc_primary(M):
    _cell_box(M, M["brushed"], M["white"])
    for x in (-0.3, 0.0, 0.3):
        box((0.04, 0.72, 0.5), (x, 0, 0.27), M["steel"])


def p_silver_zinc_rechargeable(M):
    _cell_box(M, M["navy"], M["white"])
    cyl(0.04, 0.03, (0.3, -0.36, 0.42), M["led"], (math.pi / 2, 0, 0), verts=16)
    cyl(0.08, 0.1, (0, 0.4, 0.3), M["dark"], (math.pi / 2, 0, 0))
    tube([(0, 0.45, 0.3), (0, 0.7, 0.25), (0.2, 0.95, 0.06), (0.6, 1.1, 0.06)], 0.035, M["dark"])


def p_nickel_cadmium(M):
    for i in range(3):
        for j in range(2):
            x, y = -0.32 + i * 0.32, -0.16 + j * 0.32
            cyl(0.15, 0.7, (x, y, 0.35), M["green"])
            cyl(0.1, 0.03, (x, y, 0.71), M["steel"])
            cyl(0.03, 0.05, (x, y, 0.74), M["steel"], verts=16)
    for z in (0.18, 0.52):
        box((1.0, 0.68, 0.06), (0, 0, z), M["alu"], bevel=0.02)
    box((0.3, 0.04, 0.02), (-0.16, -0.16, 0.76), M["copper"])
    box((0.3, 0.04, 0.02), (0.16, 0.16, 0.76), M["copper"])


def p_lithium_ion(M):
    box((1.2, 0.8, 0.05), (0, 0, 0.025), M["dark"], bevel=0.01)
    for x in (-0.6, 0.6):
        box((0.05, 0.8, 0.4), (x, 0, 0.2), M["dark"], bevel=0.01)
    for y in (-0.4, 0.4):
        box((1.2, 0.05, 0.4), (0, y, 0.2), M["dark"], bevel=0.01)
    for i in range(6):
        for j in range(4):
            x, y = -0.46 + i * 0.184, -0.27 + j * 0.18
            cyl(0.085, 0.4, (x, y, 0.25), M["blue"], verts=32)
            cyl(0.06, 0.02, (x, y, 0.455), M["steel"], verts=24)
    box((1.0, 0.18, 0.02), (0, -0.05, 0.49), M["pcb"])
    box((0.12, 0.1, 0.03), (0.2, -0.05, 0.51), M["chip"])
    box((1.25, 0.85, 0.05), (0.15, 0.45, 0.55), M["dark"], (0.55, 0, 0.1), bevel=0.01)


def _electronics_box(M, shell):
    box((1.1, 0.7, 0.5), (0, 0, 0.25), shell, bevel=0.03)


def p_no_thermal_protection(M):
    box((1.1, 0.7, 0.04), (0, 0, 0.02), M["alu"])
    for x in (-0.55, 0.55):
        box((0.03, 0.7, 0.5), (x, 0, 0.25), M["alu"])
    box((1.1, 0.03, 0.5), (0, 0.35, 0.25), M["alu"])
    for k in range(4):
        x = -0.36 + k * 0.24
        box((0.025, 0.6, 0.42), (x, 0, 0.25), M["pcb"])
        for c in range(3):
            box((0.02, 0.1, 0.08), (x + 0.02, -0.18 + c * 0.18, 0.3), M["chip"])
    import random
    random.seed(4)
    for _ in range(40):
        p = (random.uniform(-0.55, 0.55), random.uniform(-0.35, 0.35), random.choice([0.5, 0.46, 0.04]))
        sphere(random.uniform(0.01, 0.03), p, M["ice"])


def p_mli(M):
    _electronics_box(M, M["foil"])
    for x in (-0.25, 0.25):
        box((0.03, 0.72, 0.52), (x, 0, 0.25), M["silverfoil"])
    box((0.25, 0.12, 0.02), (0.4, -0.2, 0.5), M["black"])


def p_rhu(M):
    for k, (x, y) in enumerate([(-0.35, 0.1), (0.0, -0.1), (0.35, 0.15)]):
        cyl(0.13, 0.5, (x, y, 0.25), M["graphite"])
        sphere(0.13, (x, y, 0.5), M["graphite"], (1, 1, 0.4))
        cyl(0.135, 0.04, (x, y, 0.12), M["steel"])
        cyl(0.135, 0.04, (x, y, 0.38), M["steel"])
    cyl(0.07, 0.1, (0.15, -0.45, 0.05), M["glow"], verts=24)


def p_electric_heater(M):
    box((1.4, 0.9, 0.012), (0, 0, 0.006), M["kapton"], bevel=0.004)
    pts, rows = [], 9
    for i in range(rows):
        y = -0.36 + i * 0.09
        xs = (-0.6, 0.6) if i % 2 == 0 else (0.6, -0.6)
        pts += [(xs[0], y, 0.016), (xs[1], y, 0.016)]
    tube(pts, 0.012, M["copper"])
    tube([(-0.6, -0.36, 0.016), (-0.8, -0.36, 0.03), (-1.0, -0.3, 0.03), (-1.3, -0.15, 0.03)], 0.025, M["red"])
    tube([(-0.6, 0.36, 0.016), (-0.8, 0.36, 0.03), (-1.0, 0.25, 0.03), (-1.3, 0.05, 0.03)], 0.025, M["black"])


def p_radiator(M):
    box((1.4, 1.0, 0.04), (0, 0, 0), M["white"], bevel=0.01)
    for k in range(6):
        y = -0.4 + k * 0.16
        cyl(0.025, 1.3, (0, y, 0.04), M["alu"], (0, math.pi / 2, 0), verts=16)
    cyl(0.045, 0.95, (-0.67, 0, 0.05), M["alu"], (math.pi / 2, 0, 0), verts=20)
    for k in range(3):
        box((0.04, 0.04, 0.3), (0.5 - k * 0.5, 0.0, -0.17), M["alu"])


def p_landing_legs(M):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.35, vertices=6, location=(0, 0, 0.9))
    _finish(bpy.context.active_object, M["foil"], bevel=0.02)
    cyl(0.3, 0.1, (0, 0, 0.67), M["alu"])
    for k in range(3):
        a = 2 * math.pi * k / 3
        hip = (0.45 * math.cos(a), 0.45 * math.sin(a), 0.8)
        foot = (1.1 * math.cos(a), 1.1 * math.sin(a), 0.1)
        rod(hip, foot, 0.04, M["alu"])
        side = a + 0.6
        rod((0.4 * math.cos(side), 0.4 * math.sin(side), 0.72), foot, 0.022, M["steel"])
        side = a - 0.6
        rod((0.4 * math.cos(side), 0.4 * math.sin(side), 0.72), foot, 0.022, M["steel"])
        cone(0.12, 0.2, 0.08, (foot[0], foot[1], 0.04), M["alu"])


def p_steel_mesh_wheels(M):
    r, w, seg, rings = 0.5, 0.26, 56, 8
    verts, faces = [], []
    for i in range(rings + 1):
        t = i / rings
        y = -w / 2 + w * t
        rr = r * (0.94 + 0.06 * math.sin(math.pi * t))
        verts += [(rr * math.cos(2 * math.pi * k / seg), y, rr * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    for i in range(rings):
        a, b = i * seg, (i + 1) * seg
        faces += [(a + k, a + (k + 1) % seg, b + (k + 1) % seg, b + k) for k in range(seg)]
    tire = mesh_obj("mesh", verts, faces, M["steel"])
    wf = tire.modifiers.new("wire", "WIREFRAME")
    wf.thickness = 0.008
    for k in range(24):
        a = 2 * math.pi * k / 24
        box((0.04, w * 0.7, 0.01), (r * 1.005 * math.cos(a), 0, r * 1.005 * math.sin(a)), M["titanium"], (0, -a + math.pi / 2, 0.35))
    cyl(0.18, w * 0.9, (0, 0, 0), M["alu"], (math.pi / 2, 0, 0))
    for k in range(8):
        a = 2 * math.pi * k / 8
        rod((0.17 * math.cos(a), w / 2 - 0.02, 0.17 * math.sin(a)), (0.46 * math.cos(a), w / 2 - 0.02, 0.46 * math.sin(a)), 0.012, M["titanium"])
    torus(0.46, 0.012, (0, w / 2 - 0.02, 0), M["titanium"], (math.pi / 2, 0, 0))


def _cleated_wheel(M, loc, r, w, body, cleats, cleat_m, cleat_h=0.03, spokes=0):
    cyl(r, w, loc, body, (math.pi / 2, 0, 0), verts=48, bevel=0.01)
    x, y, z = loc
    for k in range(cleats):
        a = 2 * math.pi * k / cleats
        box((cleat_h * 2, w * 1.0, 0.018), (x + r * math.cos(a), y, z + r * math.sin(a)), cleat_m, (0, -a, 0))
    cyl(r * 0.35, w * 1.05, loc, M["steel"], (math.pi / 2, 0, 0))
    for k in range(spokes):
        a = 2 * math.pi * k / spokes
        rod((x + r * 0.35 * math.cos(a), y - w / 2 - 0.01, z + r * 0.35 * math.sin(a)),
            (x + r * 0.9 * math.cos(a), y - w / 2 - 0.01, z + r * 0.9 * math.sin(a)), 0.015, M["steel"])


def p_aluminum_wheels(M):
    _cleated_wheel(M, (0, 0, 0), 0.4, 0.4, M["alu"], 14, M["steel"], 0.035)
    rod((0, -0.2, 0), (0, -0.55, 0), 0.04, M["steel"])


def _rocker_bogie(M, frame, wheel_body, wheel_r, cleats):
    for side in (-1, 1):
        y = side * 0.62
        hubs = [(0.95, y, wheel_r), (0.0, y, wheel_r), (-0.95, y, wheel_r)]
        rocker = (0.25, y, 0.85)
        bogie = (-0.45, y, 0.62)
        rod(rocker, (0.95, y, 0.55), 0.04, frame)
        rod((0.95, y, 0.55), (0.95, y, wheel_r), 0.035, frame)
        rod(rocker, bogie, 0.04, frame)
        rod(bogie, (0.0, y, 0.45), 0.035, frame)
        rod((0.0, y, 0.45), (0.0, y, wheel_r), 0.03, frame)
        rod(bogie, (-0.95, y, 0.45), 0.035, frame)
        rod((-0.95, y, 0.45), (-0.95, y, wheel_r), 0.03, frame)
        for p in (rocker, bogie):
            cyl(0.06, 0.1, p, M["steel"], (math.pi / 2, 0, 0))
        for h in hubs:
            _cleated_wheel(M, (h[0], h[1] + side * 0.05, h[2]), wheel_r, 0.2, wheel_body, cleats, frame, 0.02, spokes=6)
    rod((0.25, -0.62, 0.85), (0.25, 0.62, 0.85), 0.045, M["steel"])
    box((1.3, 0.9, 0.06), (0.1, 0, 0.93), M["white"], bevel=0.01)


def p_rocker_bogie_aluminum(M):
    _rocker_bogie(M, M["alu"], M["alu"], 0.24, 12)


def p_rocker_bogie_titanium(M):
    _rocker_bogie(M, M["titanium"], M["brushed"], 0.28, 24)


def p_carbon_fiber_rotor(M):
    box((0.4, 0.36, 0.3), (0, 0, 0.4), M["silverfoil"], bevel=0.02)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        rod((0.15 * math.cos(a), 0.15 * math.sin(a), 0.3), (0.55 * math.cos(a), 0.55 * math.sin(a), 0.0), 0.015, M["carbon"])
    rod((0, 0, 0.55), (0, 0, 1.25), 0.03, M["steel"])
    for z, turn in ((0.95, 0.0), (1.15, math.pi / 2.6)):
        cyl(0.07, 0.07, (0, 0, z), M["steel"])
        for s in (0, math.pi):
            a = turn + s
            box((0.9, 0.1, 0.012), (0.48 * math.cos(a), 0.48 * math.sin(a), z), M["carbon"], (0.08, 0, a), bevel=0.005)
    box((0.22, 0.22, 0.012), (0, 0, 1.28), M["cell"])


def p_s_band(M):
    box((0.3, 0.3, 0.1), (0, 0, 0.05), M["alu"], bevel=0.01)
    cyl(0.03, 0.9, (0, 0, 0.5), M["alu"])
    dish(0.35, 0.09, (0, 0, 0.95), M["white"], (0.6, 0, 0.6))
    rod((0, 0, 0.95), (0.1, -0.13, 1.17), 0.012, M["steel"])
    cyl(0.04, 0.06, (0.1, -0.13, 1.18), M["dark"], (0.6, 0, 0.6))


def p_x_band(M):
    cyl(0.18, 0.2, (0, 0, 0.1), M["alu"])
    box((0.2, 0.3, 0.35), (0, 0, 0.35), M["alu"], bevel=0.02)
    cyl(0.07, 0.36, (0, 0, 0.5), M["steel"], (0, math.pi / 2, 0))
    tilt = (1.15, 0, 2.3)
    d = dish(0.75, 0.18, (0, 0, 0.6), M["foil"], tilt, thickness=0.03)
    feed = d.matrix_basis @ Vector((0, 0, 0.75))
    for k in range(3):
        a = 2 * math.pi * k / 3
        rim = d.matrix_basis @ Vector((0.7 * math.cos(a), 0.7 * math.sin(a), 0.16))
        rod(rim, feed, 0.012, M["white"])
    cone(0.07, 0.03, 0.12, feed, M["dark"], tilt)


def p_uhf_relay(M):
    cyl(0.35, 0.05, (0, 0, 0.025), M["alu"], bevel=0.01)
    cyl(0.12, 0.9, (0, 0, 0.5), M["white"])
    for k in range(4):
        tube(helix(0.13, 0.8, 1.5, k * math.pi / 2, 0.08), 0.012, M["copper"])
    sphere(0.12, (0, 0, 0.95), M["white"], (1, 1, 0.4))
    box((0.12, 0.06, 0.06), (0.3, 0, 0.08), M["dark"])


def p_agc(M):
    box((1.2, 0.55, 0.32), (0, 0.05, 0.16), M["agc"], bevel=0.015)
    for k in range(9):
        box((0.02, 0.5, 0.02), (-0.5 + k * 0.125, 0.05, 0.33), M["agc"])
    for x in (-0.62, 0.62):
        box((0.04, 0.1, 0.1), (x, 0.05, 0.16), M["steel"])
    # DSKY
    box((0.62, 0.5, 0.12), (0.05, -0.62, 0.06), M["bluegray"], bevel=0.01)
    box((0.26, 0.4, 0.01), (-0.12, -0.62, 0.125), M["black"])
    for r in range(3):
        box((0.2, 0.08, 0.005), (-0.12, -0.5 - r * 0.12, 0.132), M["display"])
    for i in range(3):
        for j in range(5):
            box((0.06, 0.06, 0.03), (0.13 + i * 0.075, -0.79 + j * 0.085, 0.13), M["white"], bevel=0.008)


def p_command_sequencer(M):
    box((1.0, 0.7, 0.45), (0, 0, 0.225), M["bluegray"], bevel=0.02)
    for k in range(5):
        cyl(0.055, 0.08, (-0.36 + k * 0.18, -0.38, 0.3), M["steel"], (math.pi / 2, 0, 0), verts=24)
        cyl(0.03, 0.09, (-0.36 + k * 0.18, -0.38, 0.3), M["dark"], (math.pi / 2, 0, 0), verts=16)
    box((0.5, 0.02, 0.15), (0, -0.355, 0.12), M["black"])
    for x in (-0.12, 0.12):
        cyl(0.06, 0.01, (x, -0.37, 0.12), M["alu"], (math.pi / 2, 0, 0))
    for k in range(7):
        box((0.9, 0.02, 0.025), (0, -0.25 + k * 0.08, 0.46), M["bluegray"])
    for x in (-0.48, 0.48):
        for y in (-0.33, 0.33):
            cyl(0.02, 0.02, (x, y, 0.455), M["steel"], verts=6)


def _board(M, w, d, pcb):
    box((w, d, 0.03), (0, 0, 0.015), pcb, bevel=0.004)


def p_rad6000(M):
    _board(M, 1.2, 0.8, M["pcb"])
    box((0.32, 0.32, 0.05), (0, 0, 0.055), M["ceramic"], bevel=0.005)
    box((0.2, 0.2, 0.01), (0, 0, 0.085), M["gold"])
    for x, y in [(-0.42, 0.22), (-0.42, -0.2), (0.4, 0.24), (0.4, -0.2), (-0.2, 0.3)]:
        box((0.16, 0.1, 0.03), (x, y, 0.045), M["chip"])
    import random
    random.seed(2)
    for _ in range(14):
        cyl(0.025, 0.06, (random.uniform(-0.5, 0.5), random.uniform(-0.35, 0.35), 0.06), M["alu"], verts=16)
    box((0.9, 0.08, 0.035), (0, -0.42, 0.03), M["gold"])


def p_rad750(M):
    _board(M, 1.3, 0.85, M["pcbblue"])
    box((0.34, 0.34, 0.06), (-0.1, 0, 0.06), M["ceramic"], bevel=0.005)
    box((0.22, 0.22, 0.012), (-0.1, 0, 0.095), M["gold"])
    for x, y in [(0.3, 0.22), (0.3, -0.22), (-0.45, 0.28), (-0.45, -0.28)]:
        box((0.18, 0.12, 0.03), (x, y, 0.045), M["chip"])
    box((0.04, 0.9, 0.35), (0.67, 0, 0.16), M["alu"], bevel=0.005)
    for y in (-0.38, 0.38):
        box((0.12, 0.05, 0.05), (0.72, y, 0.3), M["red"], bevel=0.01)
    box((0.06, 0.6, 0.05), (-0.64, 0, 0.04), M["dark"])


def p_snapdragon(M):
    _board(M, 0.7, 0.5, M["pcbblack"])
    box((0.18, 0.18, 0.03), (-0.08, 0, 0.045), M["chip"], bevel=0.003)
    box((0.12, 0.12, 0.004), (-0.08, 0, 0.062), M["steel"])
    for k in range(6):
        box((0.015, 0.16, 0.1), (0.12 + k * 0.035, 0, 0.08), M["alu"])
    box((0.24, 0.18, 0.02), (0.2, 0, 0.035), M["alu"])
    for x, y in [(-0.25, 0.15), (-0.25, -0.15)]:
        box((0.08, 0.06, 0.02), (x, y, 0.04), M["chip"])
    box((0.2, 0.06, 0.02), (-0.2, 0.22, 0.04), M["steel"])
    cyl(0.012, 0.01, (0.3, -0.2, 0.035), M["led"], verts=12)


PARTS = {
    "no-power-source": (p_no_power_source, (0, 0, 0)),
    "solar-panels": (p_solar_panels, (0, 0, 0)),
    "rtg-snap19": (p_rtg_snap19, (0, 0, 0)),
    "rtg-snap27": (p_rtg_snap27, (0, 0, 0)),
    "mmrtg": (p_mmrtg, (0, math.radians(70), 0)),
    "no-battery": (p_no_battery, (0, 0, 0)),
    "silver-zinc-primary": (p_silver_zinc_primary, (0, 0, 0)),
    "silver-zinc-rechargeable": (p_silver_zinc_rechargeable, (0, 0, 0)),
    "nickel-cadmium": (p_nickel_cadmium, (0, 0, 0)),
    "lithium-ion": (p_lithium_ion, (0, 0, 0)),
    "no-thermal-protection": (p_no_thermal_protection, (0, 0, 0)),
    "mli": (p_mli, (0, 0, 0)),
    "rhu": (p_rhu, (0, 0, 0)),
    "electric-heater": (p_electric_heater, (0, 0, 0)),
    "radiator": (p_radiator, (math.radians(-55), 0, 0)),
    "landing-legs": (p_landing_legs, (0, 0, 0)),
    "steel-mesh-wheels": (p_steel_mesh_wheels, (0, 0, math.radians(25))),
    "aluminum-wheels": (p_aluminum_wheels, (0, 0, math.radians(25))),
    "rocker-bogie-aluminum": (p_rocker_bogie_aluminum, (0, 0, 0)),
    "rocker-bogie-titanium": (p_rocker_bogie_titanium, (0, 0, 0)),
    "carbon-fiber-rotor": (p_carbon_fiber_rotor, (0, 0, 0)),
    "s-band": (p_s_band, (0, 0, 0)),
    "x-band": (p_x_band, (0, 0, 0)),
    "uhf-relay": (p_uhf_relay, (0, 0, 0)),
    "agc": (p_agc, (0, 0, 0)),
    "command-sequencer": (p_command_sequencer, (0, 0, 0)),
    "rad6000": (p_rad6000, (0, 0, 0)),
    "rad750": (p_rad750, (0, 0, 0)),
    "snapdragon": (p_snapdragon, (0, 0, 0)),
}


# ---------------------------------------------------------------- framing + render

def world_coords(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    coords = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        coords += [ev.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    return coords


def frame(cam, rot):
    objs = [o for o in bpy.context.scene.objects if o.type in {"MESH", "CURVE"}]
    pivot = bpy.data.objects.new("pivot", None)
    bpy.context.scene.collection.objects.link(pivot)
    for o in objs:
        o.parent = pivot
    pivot.rotation_euler = rot
    bpy.context.view_layer.update()

    pts = world_coords(objs)
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center, radius = (lo + hi) / 2, max((hi - lo).length / 2, 1e-3)
    s = 1.0 / radius
    pivot.scale = (s, s, s)
    pivot.location = -center * s
    bpy.context.view_layer.update()

    floor = (lo.z - center.z) * s
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, floor - 0.002))
    bpy.context.active_object.is_shadow_catcher = True

    view = Vector((1.0, -1.35, 0.85)).normalized()
    cam.rotation_euler = (-view).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    pts = world_coords(objs)
    flat = [c for p in pts for c in p]
    loc, _ = cam.camera_fit_coords(bpy.context.evaluated_depsgraph_get(), flat)
    cam.location = Vector(loc) + view * 0.55


def main():
    cam = setup_scene()
    for pid, (build, rot) in PARTS.items():
        if ONLY and pid not in ONLY:
            continue
        clear_parts()
        build(materials())
        frame(cam, rot)
        ext = "webp" if bpy.context.scene.render.image_settings.file_format == "WEBP" else "png"
        bpy.context.scene.render.filepath = f"{OUT_DIR}/{pid}.{ext}"
        bpy.ops.render.render(write_still=True)
        print(f"rendered {pid}")


main()
