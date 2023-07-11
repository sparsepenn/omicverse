import pytest 
import omicverse as ov



def test_pp():
    adata=ov.utils.pancreas()
    adata=ov.pp.qc(adata,
              tresh={'mito_perc': 0.05, 'nUMIs': 500, 'detected_genes': 250})
    ov.utils.store_layers(adata,layers='counts')
    adata=ov.pp.preprocess(adata,mode='pearson',n_HVGs=2000,)
    ov.pp.scale(adata)
    adata=ov.pp.pca(adata,layer='scaled',n_pcs=50)
    assert adata.obsm['X_pca'].shape[1]==50


def test_anno():
    adata=ov.utils.pancreas()
    adata=ov.single.scanpy_lazy(adata)
    scsa=ov.single.pySCSA(adata=adata,
                          foldchange=1.5,
                          pvalue=0.01,
                          celltype='normal',
                          target='cellmarker',
                          tissue='All',
    )
    anno=scsa.cell_anno(clustertype='leiden',
               cluster='all',rank_rep=True)
    assert anno is not None

def test_metatime():
    adata=ov.utils.pancreas()
    adata=ov.single.scanpy_lazy(adata)
    TiME_object=ov.single.MetaTiME(adata,mode='table')
    TiME_object.overcluster(resolution=8,clustercol = 'overcluster',)
    TiME_object.predictTiME(save_obs_name='MetaTiME')
    assert TiME_object.adata.obs['MetaTiME'].shape[0]==adata.shape[0]

def test_via():
    adata=ov.utils.pancreas()
    adata=ov.single.scanpy_lazy(adata)
    v0 = ov.single.pyVIA(adata=adata,adata_key='X_pca',adata_ncomps=50, basis='X_umap',
                         clusters='clusters',knn=30,random_seed=112,)

    v0.run()
    v0.get_pseudotime(v0.adata)
    assert v0.adata.obs['pt_via'].shape[0]==adata.shape[0]

def test_simba():
    adata=ov.utils.pancreas()
    adata.obs['batch']='1'
    adata.obs.loc[adata.obs.index[:1000],'batch']='2'
    simba_object=ov.single.pySIMBA(adata)
    simba_object.preprocess(batch_key='batch',min_n_cells=3,
                    method='lib_size',n_top_genes=3000,n_bins=5)
    simba_object.gen_graph()
    simba_object.train(num_workers=1)
    adata=simba_object.batch_correction()
    assert adata.obsm['X_simba'].shape[0]==adata.shape[0]
