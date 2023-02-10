import math
from app.models import Hike, Trail
from collections import defaultdict


# https://stackoverflow.com/questions/15273693/union-of-multiple-ranges
def unionize_ranges(ranges):
    unionized_ranges = []
    for begin,end in sorted(ranges):
        if unionized_ranges and unionized_ranges[-1][1] >= begin - 1:
            unionized_ranges[-1][1] = max(unionized_ranges[-1][1], end)
        else:
            unionized_ranges.append([begin, end])
    return unionized_ranges

def calculate_stats(hikes):
    trail_ranges = defaultdict(list)
    trail_lengths = {}
    for hike in hikes:
        trail = hike.path
        trail_lengths[trail.name] = trail.length
        km_start = min(hike.km_start,hike.km_end)
        km_end = max(hike.km_start,hike.km_end)
        trail_ranges[trail.name].append((km_start,km_end))
    unionized_ranges = defaultdict(list)
    for name, ranges in trail_ranges.items():
        unionized_ranges[name] = unionize_ranges(ranges)
    total_distances = {}
    percentages = {}
    for trail, ranges in unionized_ranges.items():
        total_distances[trail] = 0
        for range in ranges:
            total_distances[trail] += range[1]-range[0]
        total_distances[trail] = round(total_distances[trail],1)
        percentages[trail] = round(100*total_distances[trail]/trail_lengths[trail],1)
    return {
        'total_distances': total_distances,
        'percentages': percentages,
    }