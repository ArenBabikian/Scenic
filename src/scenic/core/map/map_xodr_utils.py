
from scenic.formats.opendrive import xodr_parser
from src.scenic.formats.opendrive.xodr_parser import Lane, Poly3


def parse_into_segmments(seg_len, road, next_sec, s, left, right):

    left_segments = {}
    right_segments = {}

    next_seg_s = road.length
    if next_sec is not None:
        next_seg_s = float(next_sec.get('s'))
    cur_section_len = next_seg_s - s

    real_seg_len = -1
    if left is not None:
        left_segments, left_seg_len = parse_lanes_to_segments(left, cur_section_len, seg_len, s)
        real_seg_len = left_seg_len # print(left_segments)

    if right is not None:
        right_segments, right_seg_len = parse_lanes_to_segments(right, cur_section_len, seg_len, s)
        real_seg_len = right_seg_len

    assert left is not None or right is not None

    if right is not None and left is not None:
        assert len(left_segments) == len(right_segments)
        assert right_seg_len == left_seg_len
    left_len = len(left_segments)
    right_len = len(right_segments)
    left_segments_at_i = {}
    right_segments_at_i = {}

    for i in range(max(left_len, right_len)):

        if left_len!= 0:
            left_segments_at_i = left_segments[i]
        if right_len != 0:
            right_segments_at_i = right_segments[i]

        # s of the laneSection is relative to the start of the road
        new_s = (i * real_seg_len) + s
        lane_segment_at_i = xodr_parser.LaneSection(new_s, left_segments_at_i, right_segments_at_i)

        # TODO do linking
        road.lane_secs.append(lane_segment_at_i)


def parse_lanes_to_segments(lanes_elem, cur_section_len, segment_len, s):
        '''Lanes_elem (of a laneSection) should be <left> or <right> element.
        Returns list dict of lane ids and Lane objects.'''

        def getNextOrInf(l, index):
            if index == len(l)-1:
                return float('inf')
            else:
                return l[index+1]

        num_segments = round(cur_section_len/segment_len)
        num_segments = 1 if num_segments == 0 else num_segments
        segment_len_real = cur_section_len/num_segments
    
        lane_segments = [{} for _ in range(num_segments)]
        # [{}] * num_segments # does not work = makes compies of the same {}
        for l in lanes_elem.iter('lane'):
            id_ = int(l.get('id'))
            type_ = l.get('type')
            link = l.find('link')
            pred = None
            succ = None
            if link is not None:
                pred_elem = link.find('predecessor')
                succ_elem = link.find('successor')
                if pred_elem is not None:
                    pred = int(pred_elem.get('id'))
                if succ_elem is not None:
                    succ = int(succ_elem.get('id'))

            widths = list(l.iter('width'))
            offsets = [float(w.get('sOffset')) for w in widths]
            # NOTE: sOffsets are supposed to (1) start from 0 at every laneSection, and (2) be increasing (so the vallue is always relative to the start of the laneSection)

            offset_start_i = 0
            offset_end_i = 0
            for i in range(num_segments):
                
                pred_seg = id_ if i != 0 else pred
                succ_seg = id_ if i != num_segments-1 else succ

                # Create a Lane pbject for each segment
                laneSegment = Lane(id_, type_, pred_seg, succ_seg)

                # Offset handling magic
                seg_start = i * segment_len_real
                seg_end = (i+1) * segment_len_real

                wo_start = offsets[offset_start_i]
                wo_end = getNextOrInf(offsets, offset_end_i)
                if wo_end == seg_start:
                    offset_start_i += 1
                    offset_end_i += 1
                    wo_start = offsets[offset_start_i]
                    wo_end = getNextOrInf(offsets, offset_end_i)

                calc_offsets = [seg_start-wo_start] # relative to the start of the segment
                local_offsets = [0] # relative to the start of the segment
                while seg_end > wo_end:
                    local_offsets.append(wo_end-seg_start)
                    calc_offsets.append(0)
                    offset_end_i += 1
                    wo_end = getNextOrInf(offsets, offset_end_i)

                # Going through list of wdths
                for j in  range(offset_start_i, offset_end_i+1):
                    w = widths[j]
                    o = local_offsets[j-offset_start_i]
                    offset = calc_offsets[j-offset_start_i]

                    a = float(w.get('a'))
                    b = float(w.get('b'))
                    c = float(w.get('c'))
                    d = float(w.get('d'))
                    a_new = a + b*offset + c*offset*offset + d*offset*offset*offset
                    b_new = b + 2*c*offset + 3*d*offset*offset
                    c_new = c + 3*d*offset
                    d_new = d
                    w_poly = Poly3(a_new, b_new, c_new, d_new)
                    laneSegment.width.append((w_poly, o))
                lane_segments[i][id_] = laneSegment
                offset_start_i = offset_end_i

        return lane_segments, segment_len_real

