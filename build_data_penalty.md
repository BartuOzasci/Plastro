```
1. build_penalty_beam_lengths(colTopo, colSpanTopo, beamTopo, axNod, nodeDist, axSpan, beamLenLimMin, beamLenLimMax)

2. build_penalty_beam_dist(beamTopo, spanDistMin, spanDistMax, beamDistMin, beamDistMax)

3. build_penalty_col_dist(colTopo, colSpanTopo, spans, nodeDist, colDistMin, colDistMax)

4. build_penalty_beam_with_free_end(colTopo, colSpanTopo, beamTopo, spans, spanLen)

5. build_data_penalty(cand, geoData, xls)
    1. build_penalty_beam_lengths(colTopo, colSpanTopo, beamTopo, axNod, nodeDist, axSpan, beamLenLimMin, beamLenLimMax)
    2. build_penalty_beam_dist(beamTopo, spanDistMin, spanDistMax, beamDistMin, beamDistMax)
    3. build_penalty_col_dist(colTopo, colSpanTopo, spans, nodeDist, colDistMin, colDistMax)
    4. build_penalty_beam_with_free_end(colTopo, colSpanTopo, beamTopo, spans, spanLen)
```