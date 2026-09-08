"""
Sample data generated at runtime -- nothing sensitive is checked into the repo.
Mirrors the role of patient_report.txt / sample.bmp in the original SHADE scripts,
but produced in code so the app has no on-disk secrets and works the same for
every user/session.
"""

import struct


SAMPLE_PATIENT_REPORT = """\
SHADE HOSPITAL NETWORK -- ELECTRONIC MEDICAL RECORD (SYNTHETIC)
=================================================================
Patient ID       : SHD-2049-A
Attending        : Dr. Kavya Sharma
Facility         : SHADE Hospital Network, Gujarat, IN
Record Type      : Telemedicine Consultation Summary

Chief Complaint
----------------
Patient presents with intermittent chest discomfort over the past 5 days,
exacerbated by exertion, relieved by rest. No prior cardiac history.

Vitals
------
BP: 128/82 mmHg   HR: 78 bpm   SpO2: 98%   Temp: 98.4 F

Assessment
----------
Findings consistent with mild exertional angina. ECG within normal limits.
Recommend outpatient stress test and lipid panel within 2 weeks.

Plan
----
1. Atorvastatin 20mg nightly
2. Follow-up telemedicine consult in 14 days
3. Referral to cardiology if symptoms persist or worsen

-- End of synthetic record. Generated for cryptographic demonstration only. --
"""


def get_sample_report(size_hint: str = "default") -> bytes:
    """
    Returns sample EMR text as bytes. size_hint scales it up for benchmark cards
    ("1kb", "100kb", "1mb") by repeating the base record, or "default" for the
    single-record version used by most cards.
    """
    base = SAMPLE_PATIENT_REPORT.encode("utf-8")
    targets = {"1kb": 1024, "100kb": 100 * 1024, "1mb": 1024 * 1024}
    if size_hint not in targets:
        return base
    target_size = targets[size_hint]
    reps = max(1, target_size // len(base) + 1)
    return (base * reps)[:target_size]


def get_sample_bmp(width: int = 64, height: int = 64) -> bytes:
    """
    Generates a small valid 24-bit BMP in code (blue background with a simple
    geometric shape), standing in for the original sample.bmp so ECB pattern
    leakage is visible without needing a checked-in binary asset.
    """
    row_padding = (4 - (width * 3) % 4) % 4
    pixel_data = bytearray()

    for y in range(height):
        for x in range(width):
            # Background: blue. Shape: a centered square in a lighter blue,
            # plus horizontal bands -- gives ECB mode plenty of repeated
            # 16-byte blocks to visibly leak.
            in_square = (width * 0.25 <= x <= width * 0.75) and (
                height * 0.25 <= y <= height * 0.75
            )
            in_band = (y // 8) % 2 == 0
            if in_square:
                b, g, r = 235, 160, 60
            elif in_band:
                b, g, r = 200, 120, 40
            else:
                b, g, r = 160, 90, 20
            pixel_data += bytes([b, g, r])
        pixel_data += bytes(row_padding)

    pixel_data_size = len(pixel_data)
    file_size = 54 + pixel_data_size

    header = b"BM" + struct.pack(
        "<IHHI", file_size, 0, 0, 54
    )
    dib_header = struct.pack(
        "<IiiHHIIiiII",
        40,          # DIB header size
        width,
        height,
        1,           # color planes
        24,          # bits per pixel
        0,           # compression (none)
        pixel_data_size,
        2835,        # x pixels per meter
        2835,        # y pixels per meter
        0,           # colors in palette
        0,           # important colors
    )
    return header + dib_header + bytes(pixel_data)


BMP_HEADER_SIZE = 54  # standard BMP header + DIB header size used throughout SHADE
