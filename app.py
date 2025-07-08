# app.py
from flask import Flask, render_template, request, send_from_directory

from utils import (
    parse_labels,
    load_gpx,
    tag_points,
    group_segments,
    create_gpx_from_segments
)

app = Flask(__name__)

# --------------------------
# Home page: ride segment recorder UI
# --------------------------
@app.route("/")
def index():
    return render_template("index.html")

# --------------------------
# GPX processor page
# --------------------------
@app.route("/process", methods=["GET", "POST"])
def process():
    if request.method == "POST":
        try:
            # Check if files are present
            if "gpx_file" not in request.files or "label_file" not in request.files:
                raise ValueError("Both a GPX file and a labels file must be uploaded.")

            gpx_file = request.files["gpx_file"]
            label_file = request.files["label_file"]

            # Check if filenames are empty
            if gpx_file.filename == "" or label_file.filename == "":
                raise ValueError("One or both files were not selected. Please upload both files.")

            # Check file extensions
            if not gpx_file.filename.lower().endswith(".gpx"):
                raise ValueError("The first file must be a GPX file (.gpx extension).")

            if not label_file.filename.lower().endswith(".txt"):
                raise ValueError("The second file must be a text file (.txt extension).")

            gpx_path = "uploaded_track.gpx"
            label_path = "uploaded_labels.txt"

            # Save uploaded files
            gpx_file.save(gpx_path)
            label_file.save(label_path)

            # Process with your helper functions
            labels = parse_labels(label_path)
            gpx = load_gpx(gpx_path)
            tagged_points = tag_points(gpx, labels)

            # Group segments
            good_segments = group_segments(tagged_points, "Good")
            bad_segments = group_segments(tagged_points, "Bad")

            # Create new GPX files
            create_gpx_from_segments(good_segments, "good_segments_multi.gpx", track_name="Good Segments")
            create_gpx_from_segments(bad_segments, "bad_segments_multi.gpx", track_name="Bad Segments")

            # Add warnings
            warnings = []
            if not good_segments:
                warnings.append("No good segments found. The Good GPX file will be empty.")
            if not bad_segments:
                warnings.append("No bad segments found. The Bad GPX file will be empty.")

            # Show download links and warnings
            return render_template("process.html", done=True, warnings=warnings)

        except Exception as e:
            # If any error occurs, show error message on page
            return render_template("process.html", done=False, error=str(e))

    # If GET, show form
    return render_template("process.html", done=False)


# --------------------------
# Download routes for GPX files
# --------------------------
@app.route("/good_segments_multi.gpx")
def download_good():
    return send_from_directory(".", "good_segments_multi.gpx", as_attachment=True)

@app.route("/bad_segments_multi.gpx")
def download_bad():
    return send_from_directory(".", "bad_segments_multi.gpx", as_attachment=True)

# --------------------------
# Run the app
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
