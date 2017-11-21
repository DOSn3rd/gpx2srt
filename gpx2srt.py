#!/bin/env python3.5

# Package dependencies:
#  haversine
#  gpxpy

import gpxpy
from haversine import haversine

import argparse, time, os

parser = argparse.ArgumentParser(
    description='Converts supported GPX files to subtitle files to be used as video overlays for "action videos"'
)
parser.add_argument("file" , help='The GPX file to convert, eg. "Current.gpx"', metavar='FILE')
#parser.add_argument("--segment", help='Index number of segment to export if the chosen track contains multiple track segments. Cannot be used without --track', type=int, default=None)
#parser.add_argument("--track", help='Index number of track to export if the file contains multiple tracks', type=int, default=None)
parser.add_argument("--output", help='The output filename to be used. Index numbers for track and segment will be appended (default: output.srt)', default="output.srt")
args = parser.parse_args()

#if args.segment and not args.track:
#    print('ERROR: --segment cannot be used without --track')
#    exit(2)

input_file = open(args.file, 'r')
gpx = gpxpy.parse(input_file)
input_file.close()

track_number = 0

for track in gpx.tracks:
    segment_number = 0
    for segment in track.segments:
        prev_point = None
        start_time = None
        line_counter = 1

        output_filename_tuple = os.path.splitext(args.output)
        output_filename_list = [ output_filename_tuple[0], '_'+str(track_number), '_'+str(segment_number), output_filename_tuple[1] ]
        output_filename = ''.join(output_filename_list)

        output_file = open(output_filename, 'w')

        for point in segment.points:

            # Problably never an actual valid point, if so, whatever.
            # The GPS unit this was built for equates (haha!) the latlong (0.0000000000, 0.0000000000) to "No satellite reception"
            if point.latitude == 0 and point.longitude == 0:
                continue

            if not start_time:
                start_time = point.time

            if prev_point:

                distance_in_km = haversine((prev_point.latitude,prev_point.longitude), (point.latitude, point.longitude))

                time_diff = point.time - prev_point.time
                speed_kmh = distance_in_km / ( time_diff.total_seconds() / 3600 )


                # Print SRT pls
                output_file.write('{0}\n'.format(line_counter))
                output_file.write('{0},000 --> {1},000\n'.format( (prev_point.time - start_time), (point.time - start_time)))
                output_file.write('({0:.1f} meters, time {1:.0f} seconds) {2:.2f} km/h\n'.format(distance_in_km*1000, time_diff.total_seconds(), speed_kmh))
                output_file.write('\n')
                output_file.write('\n')

                line_counter = line_counter + 1

            prev_point = point
        output_file.close()
        segment_number = segment_number + 1
    track_number = track_number + 1

