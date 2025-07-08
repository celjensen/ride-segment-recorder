import gpxpy
import gpxpy.gpx
from datetime import datetime

# --------------------------
# Function to parse label file
# --------------------------
def parse_labels(label_file_path):
    labels = []

    with open(label_file_path) as f:
        for line in f:
            # Each line looks like: 10:05:00 Good
            parts = line.strip().split()
            time_str = parts[0]
            state = parts[1]

            # Convert time string to time object
            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()

            # Store tuple (time, state)
            labels.append((time_obj, state))

    return labels

# --------------------------
# Function to load GPX file
# --------------------------
def load_gpx(gpx_file_path):
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    return gpx

# --------------------------
# Assign a label to each point
# --------------------------
def tag_points(gpx, labels):
    tagged_points = []

    # Start with first label
    current_state = labels[0][1]
    label_idx = 0

    # Loop through all points
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # Get time of point
                point_time = point.time.time()

                # If point time >= next label time, move to next label

                # Ensure don't go past end of list AND checks if current point's time is
                # equal to or after the next label
                while (label_idx + 1 < len(labels)) and (point_time >= labels[label_idx + 1][0]):
                    label_idx += 1
                    current_state = labels[label_idx][1]

                # Store point with its current label
                tagged_points.append((point, current_state))

    return tagged_points

# --------------------------
# Group points into segments by given label (Good or Bad)
# --------------------------
def group_segments(tagged_points, target_label):
    segments = []
    current_segment = []

    # Loop through tagged points
    for point, label in tagged_points:
        # If label matches target (Good or Bad), append
        if label == target_label:
            current_segment.append(point)
        else:
            # If current segment not empty, append to segments
            # Basically, we have finished one continuous segment of points
            if current_segment:
                segments.append(current_segment)
                current_segment = []

    # Add last segment if it ends on target label
    if current_segment:
        segments.append(current_segment)

    return segments

# --------------------------
# Create GPX file from segments
# --------------------------
def create_gpx_from_segments(segments, output_file, track_name="Segments"):
    gpx = gpxpy.gpx.GPX()
    gpx.creator = "Python GPX Splitter"

    # Create a track and add it to GPX
    track = gpxpy.gpx.GPXTrack(name=track_name)
    gpx.tracks.append(track)

    # Add each group of points as a separate track segment
    for segment_points in segments:
        segment = gpxpy.gpx.GPXTrackSegment()

        for point in segment_points:
            # Remove Garmin extensions to keep file simple and compatible
            new_point = gpxpy.gpx.GPXTrackPoint(
                point.latitude,
                point.longitude,
                elevation=point.elevation,
                time=point.time
            )
            segment.points.append(new_point)

        track.segments.append(segment)

    # Write final GPX to file
    with open(output_file, 'w') as f:
        f.write(gpx.to_xml())

# --------------------------
# Main function to run everything

# Used for testing or to run without the app
# --------------------------

'''
def main():
    label_file = "labels.txt"  # Your label file
    gpx_file = "track.gpx"     # Your original GPX file

    # Parse labels and GPX data
    labels = parse_labels(label_file)
    gpx = load_gpx(gpx_file)

    # Tag each point with Good or Bad
    tagged_points = tag_points(gpx, labels)

    # Group Good segments
    good_segments = group_segments(tagged_points, "Good")

    # Group Bad segments
    bad_segments = group_segments(tagged_points, "Bad")

    # Create GPX file with multiple Good segments
    create_gpx_from_segments(good_segments, "good_segments_multi.gpx", track_name="Good Segments")

    # Create GPX file with multiple Bad segments
    create_gpx_from_segments(bad_segments, "bad_segments_multi.gpx", track_name="Bad Segments")

    # Print summary
    print(f"Finished! Created {len(good_segments)} Good segments and {len(bad_segments)} Bad segments.")
    print("Files saved as good_segments_multi.gpx and bad_segments_multi.gpx.")

# --------------------------
# Run the program
# --------------------------
if __name__ == "__main__":
    main()
'''