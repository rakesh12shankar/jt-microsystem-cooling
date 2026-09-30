"""Spatially degraded bond, reusable FE load bases and self-consistent network.

Void conductivity is a screening ratio of effective intact bond conductivity.
No crack mechanics, interfacial radiation or void gas state is inferred.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from scipy.optimize import brentq
from package_fem import layer_mesh
from array_model import loads,die_heat
from packaging_model import ScreenCapacity


def basis(p,level=4,fraction=0.,shape='center_square',ratio=1e-4):
    if not 0<=fraction<=1 or not 0<ratio<=1:raise ValueError('Invalid defect fraction or conductivity ratio')
    if shape not in ['center_square','center_circle','edge_strip','corner_square']:raise ValueError('Unknown defect shape')
    pts,tets,regions,top,fixed=layer_mesh(p,level)
    xyz=pts[tets];a=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2)
    grad=np.linalg.inv(a)[:,1:,:];vol=np.abs(np.linalg.det(a))/6
    dx,dy=p['die_dimensions_m'][:2];nx=6*level;ny=5*level
    # Snap element centroids to in-plane cell centers: defect spans entire bond thickness.
    centroid=xyz.mean(axis=1)
    ix=np.floor((centroid[:,0]+dx/2)/(dx/nx)).astype(int)
    iy=np.floor((centroid[:,1]+dy/2)/(dy/ny)).astype(int)
    xx=(ix+.5)*dx/nx-dx/2
    yy=(iy+.5)*dy/ny-dy/2
    side=np.sqrt(fraction)
    if shape=='center_square':
        # Even cell counts keep the footprint centered; report actual area.
        wx=2*round(nx*side/2);wy=2*round(ny*side/2)
        mask=(ix>=(nx-wx)//2)&(ix<(nx+wx)//2)&(iy>=(ny-wy)//2)&(iy<(ny+wy)//2)
    elif shape=='center_circle':mask=xx**2+yy**2<dx*dy*fraction/np.pi
    elif shape=='edge_strip':mask=ix>=nx-round(nx*fraction)
    else:mask=(ix>=nx-round(nx*side))&(iy>=ny-round(ny*side))
    mask &= regions==1
    kb=p['bond_thickness_m']/(p['bond_thickness_m']/p['bond_conductivity_W_mK']+p['contact_resistivity_m2K_W'])
    ks=np.asarray([p['adapter_conductivity_W_mK'],kb,p['die_conductivity_W_mK']])[regions]
    ks[mask]*=ratio
    local=np.einsum('eai,eaj->eij',grad,grad)*(vol*ks)[:,None,None]
    K=coo_matrix((local.ravel(),(np.repeat(tets,4,axis=1).ravel(),np.tile(tets,(1,4)).ravel())),shape=(len(pts),len(pts))).tocsr()
    tri=pts[top];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
    centers=tri.mean(axis=1);hot=np.exp(-(centers[:,0]**2+centers[:,1]**2)/(2*.00035**2))
    face=np.c_[area/area.sum(),area*hot/np.dot(area,hot)]
    F=np.zeros((len(pts),2));weights=np.zeros(len(pts))
    for j in range(3):
        np.add.at(F,top[:,j],face/3);np.add.at(weights,top[:,j],area/3)
    free=np.setdiff1d(np.arange(len(pts)),fixed)
    rise=np.zeros_like(F);rise[free]=splu(K[free][:,free].tocsc()).solve(F[free])
    residual=K@rise-F;topids=np.unique(top)
    return dict(top_basis=rise[topids],mean_basis=weights@rise/weights.sum(),
                actual_fraction=float(vol[mask].sum()/vol[regions==1].sum()),requested_fraction=fraction,
                shape=shape,ratio=ratio,level=level,nodes=len(pts),
                energy_residual_per_W=np.sum(residual[fixed],axis=0)+np.sum(F,axis=0),
                points=pts,top_ids=topids,top_triangles=top)


def equilibrium(p,b,power,c=None):
    c=c or ScreenCapacity();pp={**p,'device_power_W':power}
    def mean_at(tc):
        def fun(td):
            heat=die_heat(loads(tc,td,pp))
            return td-tc-np.dot(b['mean_basis'],[heat-.5*power,.5*power])
        return brentq(fun,tc,294.99)
    def fun(tc):return c(tc)-sum(loads(tc,mean_at(tc),pp).values())
    if fun(c.minimum)>0 or fun(c.maximum)<0:raise ValueError('Equilibrium outside measured capacity branch')
    tc=brentq(fun,c.minimum,c.maximum);td=mean_at(tc);q=loads(tc,td,pp)
    top=tc+b['top_basis']@np.array([die_heat(q)-.5*power,.5*power])
    return dict(platform_K=tc,mean_K=td,peak_K=float(top.max()),nonuniformity_K=float(np.ptp(top)),
                energy_residual_W=fun(tc),power_W=power,top_temperature_K=top)


def allowable_power(p,b,c=None):
    c=c or ScreenCapacity()
    def f(power):return equilibrium(p,b,power,c)['peak_K']-p['target_K']
    if f(0)>0:return None
    # Adaptive bracket stays within measured branch for normal cases.
    upper=.01
    while f(upper)<0:
        upper*=1.5
        if upper>.2:raise ValueError('No peak boundary within power screen')
    return float(brentq(f,0,upper,xtol=1e-10))
