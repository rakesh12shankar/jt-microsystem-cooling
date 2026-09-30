"""Small reproducible finite-element solvers; scipy sparse, no commercial solver.

Thermal: linear tetrahedra in an adapter/bond/die stack.
Mechanical: linear plane-stress triangles in the bonded x-z cross-section.
Properties are effective screening assumptions in array_design.json.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

def dirichlet(K,F,fixed):
    free=np.setdiff1d(np.arange(len(F)),np.asarray(fixed))
    u=np.zeros(len(F));u[free]=spsolve(K[free][:,free],F[free])
    return u

def layer_mesh(p,level):
    nx=6*level;ny=5*level
    dx,dy=p['die_dimensions_m'][:2]
    x=np.linspace(-dx/2,dx/2,nx+1);y=np.linspace(-dy/2,dy/2,ny+1)
    thick=[p['adapter_dimensions_m'][2],p['bond_thickness_m'],p['die_dimensions_m'][2]]
    nz=[max(1,level//2),max(1,level//4),max(1,level//2)]
    z=[0.];mat=[]
    for i,(t,n) in enumerate(zip(thick,nz)):
        z.extend(np.linspace(z[-1],z[-1]+t,n+1)[1:]);mat.extend([i]*n)
    z=np.array(z);xx,yy,zz=np.meshgrid(x,y,z,indexing='ij');pts=np.c_[xx.ravel(),yy.ravel(),zz.ravel()]
    ids=np.arange(len(pts)).reshape(nx+1,ny+1,len(z));tets=[];regions=[]
    # Six tetrahedra about the 000--111 body diagonal; conforming shared faces.
    pattern=[[0,1,3,7],[0,3,2,7],[0,2,6,7],[0,6,4,7],[0,4,5,7],[0,5,1,7]]
    for i in range(nx):
        for j in range(ny):
            for k in range(len(z)-1):
                v=[ids[i,j,k],ids[i+1,j,k],ids[i,j+1,k],ids[i+1,j+1,k],ids[i,j,k+1],ids[i+1,j,k+1],ids[i,j+1,k+1],ids[i+1,j+1,k+1]]
                for pat in pattern:tets.append([v[a] for a in pat]);regions.append(mat[k])
    top=[]
    for i in range(nx):
        for j in range(ny):
            a,b,c,d=ids[i,j,-1],ids[i+1,j,-1],ids[i,j+1,-1],ids[i+1,j+1,-1]
            top.extend([[a,b,d],[a,d,c]])
    return pts,np.asarray(tets),np.asarray(regions),np.asarray(top),ids[:,:,0].ravel()

def thermal(p,level=4,total_W=.015,hotspot_W=.005,base_K=95):
    pts,tets,regions,top,fixed=layer_mesh(p,level)
    xyz=pts[tets];a=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2)
    inv=np.linalg.inv(a);grad=inv[:,1:,:];vol=np.abs(np.linalg.det(a))/6
    kbond=p['bond_thickness_m']/(p['bond_thickness_m']/p['bond_conductivity_W_mK']+p['contact_resistivity_m2K_W'])
    ks=np.array([p['adapter_conductivity_W_mK'],kbond,p['die_conductivity_W_mK']])
    local=np.einsum('eai,eaj->eij',grad,grad)*(vol*ks[regions])[:,None,None]
    rows=np.repeat(tets,4,axis=1).ravel();cols=np.tile(tets,(1,4)).ravel()
    K=coo_matrix((local.ravel(),(rows,cols)),shape=(len(pts),len(pts))).tocsr()
    tri=pts[top];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
    centers=tri.mean(axis=1);hot=np.exp(-(centers[:,0]**2+centers[:,1]**2)/(2*(.00035)**2))
    qface=(total_W-hotspot_W)*area/area.sum()+hotspot_W*area*hot/np.sum(area*hot)
    F=np.zeros(len(pts));weights=np.zeros(len(pts))
    for j in range(3):
        np.add.at(F,top[:,j],qface/3);np.add.at(weights,top[:,j],area/3)
    rise=dirichlet(K,F,fixed);reaction=K@rise-F;topids=np.unique(top)
    return {'nodes':len(pts),'elements':len(tets),'max_die_K':float(base_K+rise[topids].max()),
        'mean_die_K':float(base_K+np.dot(weights,rise)/weights.sum()),
        'die_nonuniformity_K':float(np.ptp(rise[topids])),
        'energy_residual_W':float(F.sum()+reaction[fixed].sum()),
        'points':pts,'temperature_K':base_K+rise,'top_triangles':top,'top_ids':topids,
        'uniform_analytic_R_K_W':float(sum([p['adapter_dimensions_m'][2]/p['adapter_conductivity_W_mK'],p['bond_thickness_m']/p['bond_conductivity_W_mK'],p['contact_resistivity_m2K_W'],p['die_dimensions_m'][2]/p['die_conductivity_W_mK']])/np.prod(p['die_dimensions_m'][:2]))}

def mechanical(p,level=4,cold_K=100,matched_alpha=False):
    nx=12*level;dx=p['die_dimensions_m'][0];x=np.linspace(-dx/2,dx/2,nx+1);z=[0.];mat=[]
    for i,layer in enumerate(p['mechanical_layers']):
        n=max(2,level) if i!=1 else max(1,level//2)
        z.extend(np.linspace(z[-1],z[-1]+layer['thickness_m'],n+1)[1:]);mat.extend([i]*n)
    z=np.array(z);xx,zz=np.meshgrid(x,z,indexing='ij');pts=np.c_[xx.ravel(),zz.ravel()]
    ids=np.arange(len(pts)).reshape(nx+1,len(z));tri=[];regions=[]
    for i in range(nx):
        for j in range(len(z)-1):
            a,b,c,d=ids[i,j],ids[i+1,j],ids[i,j+1],ids[i+1,j+1]
            tri.extend([[a,b,d],[a,d,c]]);regions.extend([mat[j],mat[j]])
    tri=np.asarray(tri);regions=np.array(regions);xyz=pts[tri]
    a=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);inv=np.linalg.inv(a)
    area=np.abs(np.linalg.det(a))/2;grad=inv[:,1:,:]
    B=np.zeros((len(tri),3,6))
    B[:,0,::2]=grad[:,0,:];B[:,1,1::2]=grad[:,1,:]
    B[:,2,::2]=grad[:,1,:];B[:,2,1::2]=grad[:,0,:]
    D=[];eth=[]
    for reg in regions:
        layer=p['mechanical_layers'][reg];e=layer['E_Pa'];nu=layer['nu']
        D.append(e/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]]))
        alpha=p['mechanical_layers'][0]['alpha_per_K'] if matched_alpha else layer['alpha_per_K']
        eth.append([alpha*(cold_K-295)]*2+[0])
    D=np.array(D);eth=np.array(eth);width=p['die_dimensions_m'][1]
    local=np.einsum('eai,eab,ebj->eij',B,D,B)*(area*width)[:,None,None]
    f=np.einsum('eai,eab,eb->ei',B,D,eth)*(area*width)[:,None]
    dofs=np.empty((len(tri),6),int);dofs[:,::2]=2*tri;dofs[:,1::2]=2*tri+1
    K=coo_matrix((local.ravel(),(np.repeat(dofs,6,axis=1).ravel(),np.tile(dofs,(1,6)).ravel())),shape=(2*len(pts),)*2).tocsr()
    F=np.zeros(2*len(pts));np.add.at(F,dofs.ravel(),f.ravel())
    # Pin bottom left in x,z; roller bottom right in z. Free in-plane contraction.
    fixed=[2*ids[0,0],2*ids[0,0]+1,2*ids[-1,0]+1]
    u=dirichlet(K,F,fixed);strain=np.einsum('eai,ei->ea',B,u[dofs]);stress=np.einsum('eab,eb->ea',D,strain-eth)
    vm=np.sqrt(stress[:,0]**2-stress[:,0]*stress[:,1]+stress[:,1]**2+3*stress[:,2]**2)
    mid=np.abs(xyz.mean(axis=1)[:,0])<.002
    return {'nodes':len(pts),'elements':len(tri),'points':pts,'triangles':tri,'displacement_m':u.reshape(-1,2),
        'von_mises_Pa':vm,'regions':regions,'warpage_um':float(np.ptp(u.reshape(-1,2)[ids[:,-1],1])*1e6),
        'central_die_von_mises_MPa':float(np.max(vm[mid&(regions==2)])/1e6),
        'peak_von_mises_MPa':float(vm.max()/1e6),
        'free_residual_N':float(np.max(np.abs((K@u-F)[np.setdiff1d(np.arange(len(F)),fixed)])))}
