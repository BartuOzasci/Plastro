`1. build_nodes_axMat(axes)`

    nodes = [ [175.3,213.7] , [11.2,357.3] , ... ]
    düğüm (aks kesişim) noktaları

    axMat = [ [-1,0,1,2,-1,-1] , [6,-1,8,9,-1] , ... ]
    axes listesindeki hangi aks ile hangi aksın kesişiminde nodes listesindeki hangi düğümün bulunduğunu tutan matristir. Doğal olarak simetrik bir matristir ve diyagonal elemanları -1'dir. Örneğin 0 ile 4 numaralı aksların kesişimindeki düğüm numarası axMat[0][4] şeklinde çağırılır.

`2. build_axNod(axes, axMat, nodes)`

    axNod = [ [0,2,4,7,8] , [1,3,5,12,13] , ... ]
    axes listesindeki akslar üzerindeki düğümlerin nodes listesindeki index numaraları (aksların başlangıç noktasından bitiş noktasına doğru sıralı)

`3. build_nodAx(axNod, nodes)`

    nodAx = [ [0,1] , [4,7,9] , ... ]
    nodes listesindeki düğümlerden geçen aksların axes listesindeki index numaraları

`4. build_nodeDist(axNod, nodes)`

    nodeDist = [ [-1,128,-1] , [-1,-1,493] , ... ]
    axNod listesindeki aksların üzerindeki düğümlerin birbirleri arasındaki mesafelerinin tutulduğu matristir. Doğal olarak simetrik bir matristir ve diyagonal elemanları -1'dir. Örneğin, 2 ve 7 düğümleri arasındaki mesafe nodeDist[2][7] şeklinde çağırılır. Seçilen iki düğüm aynı aks üzerinde değilse -1 döner.


***


`5. build_spans(axNod)`

    spans = [ [0,2] , [2,4] , ... ]
    axes listesindeki akslar üzerinde birbirini takip eden düğümlerin arasında kalan aks parçalarının başlangıç ve bitiş düğümlerinin nodes listesindeki index numaraları (aksların başlangıç noktasından bitiş noktasına doğru sıralı)

`6. build_nodMat(spans, nodes)`

    nodMat = [ [-1,0,3,5,-1] , [6,-1,-1,1,-1] , ... ]
    nodes listesindeki hangi düğüm ile hangi düğüm arasında spans listesindeki hangi aks parçasının tanımlı olduğunu tutan listedir. Doğal olarak simetrik bir matristir ve diyagonal elemanları -1'dir. Örneğin 2 ile 5 numaralı düğümlerin arasındaki aks parçası numarası nodMat[2][5] şeklinde çağırılır.

`7. build_axSpan(axNod, nodMat)`

    axSpan = [ [0,1,2,3] , [4,5,6,7] , ... ]
    axNod listesindeki akslar üzerinde birbirini takip eden düğümler arasında kalan aks parçalarının spans listesindeki index numaraları ile ifadesi

`8. build_nodSpan(nodes, spans)`

    nodSpan = [ [0,8] , [1,9] , ... ]
    nodes listesindeki düğümlere bağlanan aks parçaları

`9. build_spanAx(axSpan, spans)`

    spanAx = [ 2 , 2 , ... ]
    spans listesindeki aks parçalarının axes listesindeki hangi index numarasına sahip aks üzerinde bulunduğu bilgisi

`10. build_spanLen(spans, nodeDist)`

    spanLen = [ 341 , 129 , ... ]
    spans listesindeki aks parçalarının uzunluğunu tutan listedir.

`11. build_spansG(nodes, spans)`

    spansG = [ [x1,y1] , [x2,y2] , ... ]
    spans listesindeki aks parçalarının orta noktalarını (geometrik merkezlerini) tutar.

`12. build_spanDist(spans, nodAx, nodeDist)`

    spanDistMin = [ [-1,540,-1] , [-1,-1,210] , ... ]
    spanDistMax = [ [-1,541,-1] , [-1,-1,315] , ... ]
    spans listesindeki aks parçaları arasındaki en küçük ve en büyük mesafeleri tutar.
    Eğer iki aks parçası arasında bir mesafeden söz edilemiyorsa ilgili değer -1'dir.


***


`13. build_polygons(polygons_points, nodes)`

    basePol = [ 0,8,9,12,21 ]
    Oturma alanının nodes listesindeki hangi düğüm noktalarında geçen poligon olduğu bilgisi
    - aynı doğru üzerindeki ilave düğümler listede bulunmamalıdır.

    floorPol = [ 1,7,10,13,20 ]
    Kat alanının nodes listesindeki hangi düğüm noktalarında geçen poligon olduğu bilgisi

    areas = [ [0,8,9,12] , [1,2,4,6] , ... ]
    nodes listesindeki düğümler ile çevrelenen poligonlar ile tanımlanan alanları tutar.
    - Her bir alanın ardışık düğümleri aynı aks üzerinde bulunmalıdır (0-8 ve 8-9 gibi).
    - Ardışık üç veya daha fazla düğüm aynı doğru üzerinde bulunmamalıdır.
    - areas listesindeki alanlar birbirini kesmemelidir.


***


`14. build_polygonGA(nodes, polygons)`

    basePolG = [xG, yG]
    basePol poligonunun geometrik merkezi

    basePolA = 3452
    basePol poligonunun alanı

    floorPolG = [xG, yG]
    floorPol poligonunun geometrik merkezi

    floorPolA = 3452
    floorPol poligonunun alanı

    areas listesindeki alanların geometrik merkezlerini tutar.
    areasG = [ [x1,y1] , [x2,y2] , ... ]

    areas listesindeki alanların alan büyüklüklerini tutar.
    areasA = [ 1243 , 3415 , ... ]


***


`15. build_areaOnNod(axNod, areas)`

    areaOnNod = [ [0,2,4,7,8,9,12] , ... ]
    areas listesindeki alanların kenarları üzerinde bulunan noktaları tutar.

`16. build_nodOnArea(areaOnNod, nodes)`

    nodOnArea = [ [0] , [0,1,2] , ... ]
    nodes listesindeki düğüm noktalarının, areas listesindeki hangi alanların kenarlarının üzerinde bulunduğunu tutar.

`17. build_spanOnArea(areaOnNod, spans)`

    spanOnArea = [ [0,1] , [3,7] , ... ]
    spans listesindeki aks parçalarının, areas listesindeki hangi alanların kenarlarının üzerinde bulunduğunu tutar.

`18. build_areaOnSpan(spanOnArea, areas)`

    areaOnSpan = [ [0,1,2,5,6,7,8] , ... ]
    areas listesindeki alanların kenarları üzerinde bulunan aks parçalarının spans listesindeki indekslerini tutar.

`19. build_areaInNod(areas, nodes, areaOnNod)`

    areaInNod = [ [0,2,4,7,8,9,12] , ... ]
    areas listesindeki alanların içinde bulunan noktaları tutar.

`20. build_nodInArea(nodes, areaInNod)`

    nodInArea = [ [0] , [0,1,2] , ... ]
    nodes listesindeki düğüm noktalarının, areas listesindeki hangi alanların içinde bulunduğunu tutar.

`21. build_areaInSpan(polygons, nodes, spans, areaOnSpan)`

    areaInSpan = [ [0,1,2,5,6,7,8] , ... ]
    areas listesindeki alanların içinde bulunan aks parçalarının spans listesindeki indekslerini tutar.

`22. build_spanInArea(spans, areaInSpan)`

    spanInArea = [ [0,1] , [3,7] , ... ]
    spans listesindeki aks parçalarının, areas listesindeki hangi alanların içinde bulunduğunu tutar.


***


`23. build_data_geo(axes, basePol_points, floorPol_points, areas_points)`

    Planın temel geometrik verisini oluşturup bir sözlük halinde döndürür.


***


### Öneriler
- En küçük X koordinatı tüm X koordinatlarından, en küçük Y koordinatı da tüm Y koordinatlarından çıkarılarak koordinatlar normalize edilebilir.
- Bir aksın ilk ve son kesişim noktaları haricindeki kısmının tutulması (veya çizilmesi) gereksizdir. Akslar axNod listesindeki ilk ve son düğümleri arasına çizilecek ve bu düğümlerden %5 kadar taşacak çizgiler ile değiştirilebilir.