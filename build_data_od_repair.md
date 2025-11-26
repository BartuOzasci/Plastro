```
1. build_data_od_mask_contBeam_beams(beamTopo, contBeamTopo, contBeam)

2. build_data_od_mask_contBeam_colSpans(colSpanTopo, contBeamTopo, contBeam)

3. build_od_mask_remove_colSpan_beams(colSpanTopo, beamTopo)

4. build_od_mask_remove_colSpan_cols(colTopo, colSpanTopo, spans)

5. build_od_mask_remove_alone_col(colTopo, beamTopo, nodSpan)

6. build_od_mask_remove_alone_colSpan(colSpanTopo, beamTopo, spans, nodSpan)

7. build_od_mask_alone_beam(colTopo, colSpanTopo, beamTopo, spans)

8. build_data_od_repair(cand, geoData, contBeam)
    1. build_data_od_mask_contBeam_beams(beamTopo, contBeamTopo, contBeam)
    2. build_data_od_mask_contBeam_colSpans(colSpanTopo, contBeamTopo, contBeam)
    3. build_od_mask_remove_colSpan_beams(colSpanTopo, beamTopo)
    4. build_od_mask_remove_colSpan_cols(colTopo, colSpanTopo, spans)
    5. build_od_mask_remove_alone_col(colTopo, beamTopo, nodSpan)
    6. build_od_mask_remove_alone_colSpan(colSpanTopo, beamTopo, spans, nodSpan)
    7. build_od_mask_alone_beam(colTopo, colSpanTopo, beamTopo, spans)

9. apply_od_repair(cand, od_repair_mask)
```