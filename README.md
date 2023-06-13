# molecular_picture_database


### data relationship

#### finish 

Smiles 2 smiles (in same paper)

Smiles 2 paper 

Smiles 2 picture 

Paper 2 paper （with same smiles）

Paper 2 smiles

Paper 2 picture 

#### unfinish

Smiles 2 smiles （structure similarity）

picture 2 picture  (in same paper)

picture 2 picture  (structure similarity)

picture 2 smiles

picture 2 paper

![圖片](https://github.com/mahofai/molecular_picture_database/assets/47138261/7b4d4776-3ea3-4e2a-87a9-db3fd9eb149a)





```
SELECT DISTINCT mp.* FROM m_picture mp
JOIN molecular2picture m2p ON mp.m_picture_id = m2p.m_picture_id
JOIN molecular m ON m2p.SMILES = m.SMILES
WHERE m.SMILES LIKE '%CC1C(=O)C(C([C@H]%';

用Smiles 片段查找相关图片
Smiles 2 picture
```


```
SELECT DISTINCT p.* FROM paper p
JOIN m_picture mp ON p.paper_id = mp.paper_id
WHERE mp.m_picture_id IN (
  SELECT m2p.m_picture_id FROM molecular2picture m2p
  JOIN molecular m ON m2p.SMILES = m.SMILES
  WHERE m.SMILES LIKE '%C(C([C@H](O1)%'
);

# 搜索某SMILES片段相关分子图片出现过的论文
Smiles 2 paper!

```

```
SELECT*FROMm_picture WHEREpaper_id IN(SELECTpaper_id FROMpaper WHEREtitle LIKE'%Mechanisms%')

搜索标题包含“Mechanisms”论文里出现的分子图片
Paper2picture!

```

```
SELECT DISTINCT m.SMILES
FROM molecular m
JOIN molecular2picture m2p ON m.SMILES = m2p.SMILES
JOIN m_picture mp ON m2p.m_picture_id = mp.m_picture_id
JOIN paper p ON mp.paper_id = p.paper_id
WHERE p.title LIKE '%Mechanistic%'

根据文章标题查找相关分子smiles
Paper 2 smiles!

```

```
SELECT DISTINCT m.SMILES
FROM molecular m
JOIN molecular2picture m2p ON m.SMILES = m2p.SMILES
JOIN m_picture mp ON m2p.m_picture_id = mp.m_picture_id
WHERE paper_id IN (
    SELECT DISTINCT mp.paper_id FROM m_picture mp
    JOIN molecular2picture m2p ON mp.m_picture_id = m2p.m_picture_id
    JOIN molecular m ON m2p.SMILES = m.SMILES
    WHERE m.SMILES LIKE '%C(N)([R14])[R]%'
);

根据smiles查找出现在同一文章中的其他smiles
Smiles 2 smiles!
```

```
SELECT DISTINCT p.*
FROM paper p
JOIN m_picture mp ON p.paper_id = mp.paper_id
JOIN molecular2picture mmp ON mp.m_picture_id = mmp.m_picture_id
JOIN molecular m ON mmp.SMILES = m.SMILES
WHERE m.SMILES IN (
    SELECT m2.SMILES FROM paper p2
    JOIN m_picture mp2 ON p2.paper_id = mp2.paper_id
    JOIN molecular2picture mmp2 ON mp2.m_picture_id = mmp2.m_picture_id
    JOIN molecular m2 ON mmp2.SMILES = m2.SMILES
    WHERE p2.title = ' The tryptophan oxidation pathway in mosquitoes with emphasis on xanthurenic acid biosynthesis'
)
;

Paper 2 paper![圖片](https://github.com/mahofai/molecular_picture_database/assets/47138261/da72be53-2fc5-4730-98c9-7c4fa6294566)

```





