"""Retain source zero-thickness planar artifacts without inventing solid thickness."""
from native_hardware import *
import trimesh,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union,triangulate
def add_sheets(doc,source,cad_mesh,z):
    def planar_coverage(m):
        ts=m.triangles[np.max(abs(m.triangles[:,:,2]-z),axis=1)<1e-4]
        return unary_union([p for t in ts if (p:=Polygon(t[:,:2])).area>1e-10])
    diff=planar_coverage(source)-planar_coverage(cad_mesh);polys=list(diff.geoms) if hasattr(diff,'geoms') else [diff];rows=[]
    for k,poly in enumerate(polys):
        if poly.area<1e-5:continue
        poly=poly.simplify(.00002,preserve_topology=True)
        doc.ClearSelection2(True);sm=typed(doc.SketchManager,'ISketchManager');sm.Insert3DSketch(True);sm.AddToDB=True;sm.DisplayWhenAdded=False
        for ring in [poly.exterior,*poly.interiors]:
            coords=list(ring.coords)
            for a,b in zip(coords,coords[1:]):
                if np.linalg.norm(np.array(a)-b)<1e-6:continue
                line=sm.CreateLine(a[0]/1000,a[1]/1000,z/1000,b[0]/1000,b[1]/1000,z/1000);assert line is not None,(k,a,b)
        sm.DisplayWhenAdded=True;sm.AddToDB=False;doc.SketchAddConstraints('sgFIXED');sm.Insert3DSketch(True);sketch=typed(doc.FeatureByPositionReverse(0),'IFeature');sketch.Name=f'Source_zero_thickness_patch_{k+1}_profile';doc.ClearSelection2(True);sketch.Select2(False,0)
        success=doc.InsertPlanarRefSurface();features=[];omitted=[]
        if success:
            feature=typed(doc.FeatureByPositionReverse(0),'IFeature');feature.Name=f'Source_zero_thickness_patch_{k+1}_UNVERIFIED_physical';features.append(feature.Name)
        else:
            triangles=[t for t in triangulate(poly) if poly.covers(t.representative_point())]
            assert abs(sum(t.area for t in triangles)-poly.area)<1e-8
            for j,tri in enumerate(triangles):
                doc.ClearSelection2(True);sm.Insert3DSketch(True);sm.AddToDB=True;sm.DisplayWhenAdded=False;coords=list(tri.exterior.coords)
                for a,b in zip(coords,coords[1:]):assert sm.CreateLine(a[0]/1000,a[1]/1000,z/1000,b[0]/1000,b[1]/1000,z/1000) is not None
                sm.DisplayWhenAdded=True;sm.AddToDB=False;sm.Insert3DSketch(True);sk=typed(doc.FeatureByPositionReverse(0),'IFeature');sk.Name=f'Source_patch_{k+1}_facet_{j+1}_profile';doc.ClearSelection2(True);assert sk.Select2(False,0)
                if not doc.InsertPlanarRefSurface():
                    altitude=2*tri.area/max(np.linalg.norm(np.diff(np.array(coords),axis=0),axis=1));assert altitude<.00005,(k,j,altitude)
                    omitted.append({'triangle':j,'altitude_mm':altitude,'reason':'Below native sheet feature tolerance; acceptance still requires full sampled exterior comparison'});continue
                f=typed(doc.FeatureByPositionReverse(0),'IFeature');f.Name=f'Source_zero_thickness_patch_{k+1}_facet_{j+1}';features.append(f.Name)
        rows.append({'features':features,'source_plane_z_mm':z,'area_mm2':poly.area,'source_polygon_xy_mm':list(poly.exterior.coords),'omitted_numerical_slivers':omitted,'physical_thickness':'ZERO in source geometry; manufacturability UNVERIFIED'})
    doc.ClearSelection2(True);return rows
