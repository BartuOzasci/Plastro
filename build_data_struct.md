```
1. calc_colSecProp(colSec)

2. calc_colRotated(colTopo, colSize, colDirec, axesAngle, nodAx, colSecProp)

3. calc_colPlaced(colTopo, colEccL, colEccS, nodes, colRotated)

4. calc_colSpanProp(colSpanTopo, colSpanSize, spanLen, colSpanSec)

5. calc_colSpanRotated(colSpanTopo, axesAngle, spanAx, colSpanProp)

6. calc_colSpanPlaced(colSpanTopo, colSpanEcc, spansG, colSpanRotated)

7. calc_beamPlaced(beamTopo, beamSize, beamEcc, axesAngle, nodes, spans, spanAx, spansG, beamSec)

8. calc_slabProp(geoData, dxf, xls)

9. calc_slabPlaced(slabSize, slabProp, slabSec)

10. build_data_struct(designVec, xls, geoData, colSecProp, slabProp)
    2. calc_colRotated(colTopo, colSize, colDirec, axesAngle, nodAx, colSecProp)
    3. calc_colPlaced(colTopo, colEccL, colEccS, nodes, colRotated)
    4. calc_colSpanProp(colSpanTopo, colSpanSize, spanLen, colSpanSec)
    5. calc_colSpanRotated(colSpanTopo, axesAngle, spanAx, colSpanProp)
    6. calc_colSpanPlaced(colSpanTopo, colSpanEcc, spansG, colSpanRotated)
    7. calc_beamPlaced(beamTopo, beamSize, beamEcc, axesAngle, nodes, spans, spanAx, spansG, beamSec)
    9. calc_slabPlaced(slabSize, slabProp, slabSec)
```